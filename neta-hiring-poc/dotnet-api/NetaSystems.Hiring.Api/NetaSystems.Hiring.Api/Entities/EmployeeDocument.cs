using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace NetaSystems.Hiring.Api.Entities
{
    [Table("EmployeeDocuments")]
    public class EmployeeDocument
    {
        [Key]
        public long Id { get; set; }

        [Required]
        public long EmployeeId { get; set; }

        [ForeignKey(nameof(EmployeeId))]
        public virtual Employee Employee { get; set; } = default!;

        [Required]
        [MaxLength(100)]
        public string DocumentType { get; set; } = default!;

        [Required]
        [MaxLength(255)]
        public string OriginalFileName { get; set; } = default!;

        [Required]
        [MaxLength(500)]
        public string StorageKey { get; set; } = default!;

        [Required]
        [MaxLength(100)]
        public string MimeType { get; set; } = default!;

        [Required]
        public long SizeBytes { get; set; }

        [Required]
        public DateTime UploadedAtUtc { get; set; } = DateTime.UtcNow;
    }
}