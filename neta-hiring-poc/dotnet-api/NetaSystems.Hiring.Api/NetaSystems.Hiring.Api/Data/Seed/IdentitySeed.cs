using Microsoft.AspNetCore.Identity;
using NetaSystems.Hiring.Api.Entities;

namespace NetaSystems.Hiring.Api.Data.Seed;

public static class IdentitySeed
{
    public static async Task SeedAsync(IServiceProvider services)
    {
        using var scope = services.CreateScope();

        var userManager = scope.ServiceProvider
            .GetRequiredService<UserManager<ApplicationUser>>();

        var roleManager = scope.ServiceProvider
            .GetRequiredService<RoleManager<IdentityRole<long>>>();

        const string adminRole = "Admin";

        if (!await roleManager.RoleExistsAsync(adminRole))
        {
            await roleManager.CreateAsync(
                new IdentityRole<long>(adminRole)
            );
        }

        const string email = "admin@neta.local";
        const string password = "Neta1234";

        var existingUser = await userManager.FindByEmailAsync(email);

        if (existingUser != null)
            return;

        var user = new ApplicationUser
        {
            FullName = "Administrador POC",
            UserName = email,
            Email = email,
            EmailConfirmed = true,
            IsActive = true
        };

        var result = await userManager.CreateAsync(user, password);

        if (!result.Succeeded)
        {
            var errors = string.Join(", ",
                result.Errors.Select(x => x.Description));

            throw new Exception(
                $"Error creando usuario seed: {errors}"
            );
        }

        await userManager.AddToRoleAsync(user, adminRole);
    }
}