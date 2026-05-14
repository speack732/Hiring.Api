using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using NetaSystems.Hiring.Api.DTOs;
using NetaSystems.Hiring.Api.Entities;
using NetaSystems.Hiring.Api.Services;

namespace NetaSystems.Hiring.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly JwtTokenService _jwtTokenService;
    private readonly IConfiguration _configuration;

    public AuthController(
        UserManager<ApplicationUser> userManager,
        JwtTokenService jwtTokenService,
        IConfiguration configuration)
    {
        _userManager = userManager;
        _jwtTokenService = jwtTokenService;
        _configuration = configuration;
    }

    [HttpPost("register")]
    [AllowAnonymous]
    public async Task<IActionResult> Register(RegisterRequest request)
    {
        var user = new ApplicationUser
        {
            FullName = request.FullName,
            UserName = request.Email,
            Email = request.Email,
            EmailConfirmed = true
        };

        var result = await _userManager.CreateAsync(user, request.Password);

        if (!result.Succeeded)
            return BadRequest(result.Errors);

        return Ok(new
        {
            user.Id,
            user.FullName,
            user.Email
        });
    }

    [HttpPost("login")]
    [AllowAnonymous]
    public async Task<ActionResult<AuthResponse>> Login(LoginRequest request)
    {
        var user = await _userManager.FindByEmailAsync(request.Email);

        if (user == null || !user.IsActive)
            return Unauthorized("Credenciales inválidas.");

        var isValidPassword = await _userManager.CheckPasswordAsync(
            user,
            request.Password
        );

        if (!isValidPassword)
            return Unauthorized("Credenciales inválidas.");

        var token = await _jwtTokenService.GenerateTokenAsync(user);

        var expiresMinutes = int.Parse(
            _configuration["Jwt:ExpiresMinutes"] ?? "60"
        );

        return Ok(new AuthResponse
        {
            AccessToken = token,
            TokenType = "Bearer",
            ExpiresInMinutes = expiresMinutes
        });
    }
}