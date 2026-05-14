using Microsoft.AspNetCore.Http;

namespace NetaSystems.Hiring.Api.DTOs;

public class CreateEmployeeRequest
{
    public string FirstName { get; set; } = default!;
    public string LastName { get; set; } = default!;
    public string? MiddleName { get; set; }
    public string Curp { get; set; } = default!;
    public string Rfc { get; set; } = default!;
    public string Email { get; set; } = default!;
    public string PhoneNumber { get; set; } = default!;
    public string? Address { get; set; }
    public DateTime BirthDate { get; set; }

    public IFormFile Document1 { get; set; } = default!;
    public IFormFile Document2 { get; set; } = default!;
}