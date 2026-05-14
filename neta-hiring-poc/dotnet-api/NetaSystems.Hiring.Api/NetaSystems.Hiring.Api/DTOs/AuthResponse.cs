namespace NetaSystems.Hiring.Api.DTOs;

public class AuthResponse
{
    public string AccessToken { get; set; } = default!;
    public string TokenType { get; set; } = "Bearer";
    public int ExpiresInMinutes { get; set; }
}