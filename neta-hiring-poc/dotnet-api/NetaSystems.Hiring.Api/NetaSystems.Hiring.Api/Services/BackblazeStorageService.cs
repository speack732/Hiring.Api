using Amazon.S3;
using Amazon.S3.Model;
using Microsoft.Extensions.Options;
using NetaSystems.Hiring.Api.Configuration;

namespace NetaSystems.Hiring.Api.Services;

public class BackblazeStorageService
{
    private readonly IAmazonS3 _s3Client;
    private readonly BackblazeOptions _options;

    public BackblazeStorageService(IOptions<BackblazeOptions> options)
    {
        _options = options.Value;

        var config = new AmazonS3Config
        {
            ServiceURL = _options.ServiceUrl,
            ForcePathStyle = true
        };

        _s3Client = new AmazonS3Client(
            _options.AccessKey,
            _options.SecretKey,
            config
        );
    }

    public async Task<string> UploadAsync(
        IFormFile file,
        string key,
        CancellationToken cancellationToken = default)
    {
        await using var stream = file.OpenReadStream();

        var request = new PutObjectRequest
        {
            BucketName = _options.BucketName,
            Key = key,
            InputStream = stream,
            ContentType = file.ContentType
        };

        await _s3Client.PutObjectAsync(request, cancellationToken);

        return key;
    }
}