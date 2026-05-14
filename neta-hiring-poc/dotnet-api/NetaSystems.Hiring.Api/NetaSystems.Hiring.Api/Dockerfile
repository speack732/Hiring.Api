FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src

COPY ["NetaSystems.Hiring.Api/NetaSystems.Hiring.Api.csproj", "NetaSystems.Hiring.Api/"]

RUN dotnet restore "NetaSystems.Hiring.Api/NetaSystems.Hiring.Api.csproj"

COPY . .

WORKDIR "/src/NetaSystems.Hiring.Api"

RUN dotnet build "NetaSystems.Hiring.Api.csproj" \
    -c $BUILD_CONFIGURATION \
    -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release

RUN dotnet publish "NetaSystems.Hiring.Api.csproj" \
    -c $BUILD_CONFIGURATION \
    -o /app/publish \
    /p:UseAppHost=false

FROM base AS final
WORKDIR /app

COPY --from=publish /app/publish .

ENTRYPOINT ["dotnet", "NetaSystems.Hiring.Api.dll"]