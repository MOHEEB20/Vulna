# Security Policy

## Data Privacy & Processing

### Local Processing (Default)
- All HTTP request analysis happens locally using Ollama
- No external data transmission required for core functionality
- Complete control over processed data

### Optional Cloud Features
- GPU-accelerated analysis (Enterprise Beta only)
- Explicit opt-in required
- Data encrypted in transit (TLS 1.3)
- No persistent storage of customer data
- Processing data deleted immediately after analysis

## Security Architecture

### Network Security
- Proxy runs on localhost (127.0.0.1) by default
- No external network access required for basic operation
- All external connections clearly documented

### Data Handling
- HTTP requests/responses processed in memory
- Optional local storage in SQLite (encrypted at rest)
- No telemetry or usage tracking without consent

### Vulnerability Reporting

If you discover a security vulnerability, please report it to:
- **Email**: security@keyvan.ai
- **Response Time**: Within 48 hours
- **Disclosure**: Responsible disclosure policy followed

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Security Best Practices

When using VULNA:
1. Run in isolated environment for sensitive targets
2. Review generated PoCs before execution
3. Use latest version for security updates
4. Configure firewall rules for proxy access