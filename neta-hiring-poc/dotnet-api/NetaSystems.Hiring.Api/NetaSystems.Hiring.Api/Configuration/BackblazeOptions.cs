namespace NetaSystems.Hiring.Api.Configuration
{
    public class BackblazeOptions
    {
        public string ServiceUrl { get; set; } = default!;
        public string BucketName { get; set; } = default!;
        public string AccessKey { get; set; } = default!;
        public string SecretKey { get; set; } = default!;
    }
}
