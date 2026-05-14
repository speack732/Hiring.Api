using Microsoft.AspNetCore.Identity;

namespace NetaSystems.Hiring.Api.Entities;

public class ApplicationUser : IdentityUser<long>
{
    public string FullName { get; set; } = default!;
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
}