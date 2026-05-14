using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace NetaSystems.Hiring.Api.Entities
{
    [Table("Employees")]
    public class Employee
    {
        [Key]
        public long Id { get; set; }

        [Required]
        [MaxLength(150)]
        public string FirstName { get; set; } = default!;

        [Required]
        [MaxLength(150)]
        public string LastName { get; set; } = default!;

        [MaxLength(150)]
        public string? MiddleName { get; set; }

        [Required]
        [MaxLength(18)]
        public string Curp { get; set; } = default!;

        [Required]
        [MaxLength(13)]
        public string Rfc { get; set; } = default!;

        [Required]
        [MaxLength(150)]
        public string Email { get; set; } = default!;

        [Required]
        [MaxLength(20)]
        public string PhoneNumber { get; set; } = default!;

        [MaxLength(500)]
        public string? Address { get; set; }

        [Required]
        public DateTime BirthDate { get; set; }

        [Required]
        public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;

        [MaxLength(100)]
        public string? CreatedBy { get; set; }

        public virtual ICollection<EmployeeDocument> Documents { get; set; }
            = new List<EmployeeDocument>();
    }
}