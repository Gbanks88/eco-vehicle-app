# Namecheap DNS Management Guide for CG4F.online

## Current DNS Configuration

### Domain Information
- Domain: `cg4f.online`
- Nameservers:
  - dns1.registrar-servers.com
  - dns2.registrar-servers.com

### DNS Records
1. Root Domain (A Record):
   - Host: `@`
   - Value: `57.128.180.184`
   - TTL: 1800 seconds

2. API Subdomain (A Record):
   - Host: `api`
   - Value: `57.128.180.184`
   - TTL: 3600 seconds

3. CDN Subdomain (CNAME Record):
   - Host: `cdn`
   - Value: `cg4l.site`
   - TTL: 1800 seconds

## Managing DNS Records

### Accessing Namecheap DNS Management
1. Go to [Namecheap Login](https://www.namecheap.com/myaccount/login/)
2. Navigate to Domain List → cg4f.online → Manage
3. Click on "Advanced DNS" tab

### Adding New Records
1. Click "Add New Record"
2. Choose record type:
   - A Record: Direct IP address
   - CNAME: Domain alias
   - TXT: Text records (verification, SPF)
   - MX: Email servers
3. Fill in:
   - Host: Subdomain or @ for root
   - Value: IP or domain
   - TTL: Time to live (1800 recommended)

### Common DNS Operations

#### Adding a Subdomain
```
Type: A Record
Host: subdomain
Value: Your-IP-Address
TTL: 1800
```

#### Setting Up Email
```
Type: MX Record
Host: @
Value: mail-server.domain.com
Priority: 10
TTL: 1800
```

#### Domain Verification
```
Type: TXT Record
Host: @
Value: verification-code
TTL: 1800
```

## Best Practices

1. **TTL Settings**
   - Use 1800-3600 seconds for stable records
   - Lower TTL (300-600) when planning changes
   - Increase TTL after confirming changes

2. **Security**
   - Add CAA records if using SSL
   - Implement SPF records for email
   - Use DKIM for email authentication

3. **Monitoring**
   - Regularly verify DNS propagation
   - Monitor SSL certificate expiry
   - Check for unauthorized changes

## Verification Commands

### Check DNS Propagation
```bash
# Check A Records
dig +short cg4f.online
dig +short api.cg4f.online

# Check CNAME Record
dig +short cdn.cg4f.online

# Check Nameservers
dig ns cg4f.online

# Full DNS Information
dig +trace cg4f.online
```

### SSL Verification
```bash
# Check HTTPS
curl -I https://cg4f.online

# Test SSL Certificate
openssl s_client -connect cg4f.online:443
```

## Troubleshooting

1. **DNS Not Resolving**
   - Verify nameserver configuration
   - Check record syntax
   - Wait for propagation (up to 48 hours)
   - Clear local DNS cache

2. **SSL Issues**
   - Verify A/CNAME records
   - Check CAA records if present
   - Ensure correct domain ownership

3. **Email Problems**
   - Verify MX records
   - Check SPF/DKIM records
   - Test email delivery

## Support

- Namecheap Support: https://www.namecheap.com/support/
- DNS Tool: https://www.namecheap.com/domains/dns-checker/
- Knowledge Base: https://www.namecheap.com/support/knowledgebase/
