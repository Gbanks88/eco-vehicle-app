# Eco Vehicle Project

## Infrastructure Overview

### Domain and DNS
- Domain: `cg4f.online`
- DNS Provider: Namecheap (included with domain registration)
- DNS Management: [Namecheap DNS Guide](docs/namecheap_dns_guide.md)

### Current DNS Configuration
- Root domain (A Record): `cg4f.online` → `57.128.180.184`
- API subdomain (A Record): `api.cg4f.online` → `57.128.180.184`
- CDN subdomain (CNAME): `cdn.cg4f.online` → `cg4l.site`

## Project Structure
```
eco_vehicle_project/
├── config/               # Configuration files
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── src/                 # Source code
├── tests/               # Test files
└── web/                 # Web interface
```

## Getting Started

1. Clone the repository
```bash
git clone <repository-url>
cd eco_vehicle_project
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server
```bash
python src/main.py
```

## Documentation
- [Development Guide](docs/DEVELOPMENT.md)
- [DNS Management](docs/namecheap_dns_guide.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Contributing
Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
