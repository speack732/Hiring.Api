using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using NetaSystems.Hiring.Api.Data;
using NetaSystems.Hiring.Api.DTOs;
using NetaSystems.Hiring.Api.Entities;
using NetaSystems.Hiring.Api.Services;

namespace NetaSystems.Hiring.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class EmployeesController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly BackblazeStorageService _storage;
    private readonly ILogger<EmployeesController> _logger;

    public EmployeesController(
        AppDbContext db,
        BackblazeStorageService storage,
        ILogger<EmployeesController> logger)
    {
        _db = db;
        _storage = storage;
        _logger = logger;
    }

    [HttpPost]
    [RequestSizeLimit(20_000_000)]
    
    public async Task<IActionResult> Create(
        [FromForm] CreateEmployeeRequest request,
        CancellationToken cancellationToken)
    {
        if (request.Document1 == null || request.Document1.Length == 0)
            return BadRequest("El documento 1 es requerido.");

        if (request.Document2 == null || request.Document2.Length == 0)
            return BadRequest("El documento 2 es requerido.");

        ValidateFileOrThrow(request.Document1);
        ValidateFileOrThrow(request.Document2);

        var exists = await _db.Employees.AnyAsync(x =>
            x.Curp == request.Curp || x.Rfc == request.Rfc,
            cancellationToken);

        if (exists)
            return Conflict("Ya existe un empleado con el mismo CURP o RFC.");

        await using var transaction =
            await _db.Database.BeginTransactionAsync(cancellationToken);

        try
        {
            var employee = new Employee
            {
                FirstName = request.FirstName.Trim(),
                LastName = request.LastName.Trim(),
                MiddleName = request.MiddleName?.Trim(),
                Curp = request.Curp.Trim().ToUpperInvariant(),
                Rfc = request.Rfc.Trim().ToUpperInvariant(),
                Email = request.Email.Trim(),
                PhoneNumber = request.PhoneNumber.Trim(),
                Address = request.Address?.Trim(),
                BirthDate = request.BirthDate,
                CreatedAtUtc = DateTime.UtcNow,
                CreatedBy = User.Identity?.Name
            };

            _db.Employees.Add(employee);
            await _db.SaveChangesAsync(cancellationToken);

            var document1Key = BuildStorageKey(
                employee.Id,
                "documento-1",
                request.Document1.FileName);

            var document2Key = BuildStorageKey(
                employee.Id,
                "documento-2",
                request.Document2.FileName);

            await _storage.UploadAsync(
                request.Document1,
                document1Key,
                cancellationToken);

            await _storage.UploadAsync(
                request.Document2,
                document2Key,
                cancellationToken);

            employee.Documents.Add(new EmployeeDocument
            {
                EmployeeId = employee.Id,
                DocumentType = "Document1",
                OriginalFileName = request.Document1.FileName,
                StorageKey = document1Key,
                MimeType = request.Document1.ContentType,
                SizeBytes = request.Document1.Length,
                UploadedAtUtc = DateTime.UtcNow
            });

            employee.Documents.Add(new EmployeeDocument
            {
                EmployeeId = employee.Id,
                DocumentType = "Document2",
                OriginalFileName = request.Document2.FileName,
                StorageKey = document2Key,
                MimeType = request.Document2.ContentType,
                SizeBytes = request.Document2.Length,
                UploadedAtUtc = DateTime.UtcNow
            });

            await _db.SaveChangesAsync(cancellationToken);
            await transaction.CommitAsync(cancellationToken);

            _logger.LogInformation(
                "Employee {EmployeeId} created with 2 documents",
                employee.Id);

            return CreatedAtAction(
                nameof(GetById),
                new { id = employee.Id },
                new
                {
                    employee.Id,
                    employee.FirstName,
                    employee.LastName,
                    employee.MiddleName,
                    employee.Curp,
                    employee.Rfc,
                    Documents = employee.Documents.Select(d => new
                    {
                        d.Id,
                        d.DocumentType,
                        d.OriginalFileName,
                        d.StorageKey,
                        d.SizeBytes
                    })
                });
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync(cancellationToken);

            _logger.LogError(
                ex,
                "Error creating employee with documents");

            return StatusCode(
                StatusCodes.Status500InternalServerError,
                "Ocurrió un error registrando el empleado.");
        }
    }





    [HttpGet("{id:long}")]
    public async Task<IActionResult> GetById(
        long id,
        CancellationToken cancellationToken)
    {
        var employee = await _db.Employees
            .Include(x => x.Documents)
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken);

        if (employee == null)
            return NotFound();

        return Ok(new
        {
            employee.Id,
            employee.FirstName,
            employee.LastName,
            employee.MiddleName,
            employee.Curp,
            employee.Rfc,
            employee.Email,
            employee.PhoneNumber,
            employee.CreatedAtUtc,
            Documents = employee.Documents.Select(d => new
            {
                d.Id,
                d.DocumentType,
                d.OriginalFileName,
                d.MimeType,
                d.SizeBytes,
                d.UploadedAtUtc
            })
        });
    }

    private static void ValidateFileOrThrow(IFormFile file)
    {
        var allowedContentTypes = new[]
        {
            "application/pdf",
            "image/jpeg",
            "image/png"
        };

        if (!allowedContentTypes.Contains(file.ContentType))
            throw new InvalidOperationException(
                $"Tipo de archivo no permitido: {file.ContentType}");

        const long maxSizeBytes = 10 * 1024 * 1024;

        if (file.Length > maxSizeBytes)
            throw new InvalidOperationException(
                "El archivo excede el tamaño máximo permitido de 10 MB.");
    }

    private static string BuildStorageKey(
        long employeeId,
        string documentType,
        string originalFileName)
    {
        var extension = Path.GetExtension(originalFileName);
        var safeFileName = $"{Guid.NewGuid():N}{extension}";

        return $"employees/{employeeId}/{documentType}/{safeFileName}";
    }
}