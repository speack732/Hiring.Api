using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NetaSystems.Hiring.Api.Data;

namespace NetaSystems.Hiring.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class EmployeesController : ControllerBase
{
    private readonly AppDbContext _db;

    public EmployeesController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet("test")]
    public IActionResult Test()
    {
        return Ok("JWT válido. Acceso autorizado.");
    }
}