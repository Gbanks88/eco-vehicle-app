# IBM Cloud DNS Setup Guide for CG4F.online

## 1. Initial Setup

### 1.1 Access IBM Cloud Console
1. Visit https://cloud.ibm.com
2. Sign in with your IBM Cloud credentials
3. Select the default resource group

### 1.2 Create DNS Service
1. Navigate to Catalog > Network > DNS Services
2. Configure service:
   - Name: `cg4f-dns`
   - Plan: Free
   - Region: us-south
   - Resource group: default
3. Click "Create"

## 2. DNS Zone Configuration

### 2.1 Create DNS Zone
1. In DNS Services dashboard, click "Create DNS zone"
2. Enter details:
   ```
   Domain: cg4f.online
   Label: production
   Description: Production DNS zone for CG4F Online
   ```

### 2.2 Add DNS Records
1. In the zone details, click "Add Resource Record"
2. Add the following records:

   ```
   # Root domain
   Type: A
   Name: @
   IP: 57.128.180.184
   TTL: 1800 seconds

   # API subdomain
   Type: A
   Name: api
   IP: 57.128.180.184
   TTL: 3600 seconds

   # CDN subdomain
   Type: CNAME
   Name: cdn
   Alias: cg4l.site
   TTL: 1800 seconds
   ```

## 3. Security Configuration

### 3.1 Create CIS Instance
1. Navigate to Catalog > Network > Internet Services
2. Configure service:
   - Name: `cg4f-cis`
   - Plan: Standard
   - Resource group: default
3. Click "Create"

### 3.2 Configure SSL/TLS
1. In CIS dashboard, go to Security > SSL/TLS
2. Enable Universal SSL
3. Set minimum TLS version to 1.2
4. Enable HSTS with:
   ```
   max-age: 31536000
   Include subdomains: Yes
   Preload: Yes
   ```

### 3.3 Security Settings
1. Enable Web Application Firewall (WAF)
   - Set security level to High
   - Enable OWASP rules
   - Configure rate limiting:
     ```
     Threshold: 100 requests
     Period: 60 seconds
     ```

2. Configure Page Rules:
   ```
   URL: *cg4f.online/*
   Settings:
   - Always use HTTPS
   - Browser Cache TTL: 4 hours
   - Security Level: High
   ```

## 4. Verification Steps

### 4.1 DNS Verification
```bash
# Check A records
dig @ns1.ibm.cloud cg4f.online
dig @ns1.ibm.cloud api.cg4f.online

# Check CNAME record
dig @ns1.ibm.cloud cdn.cg4f.online

# Verify nameserver propagation
dig ns cg4f.online
```

### 4.2 SSL Verification
```bash
# Check HTTPS setup
curl -I https://cg4f.online
curl -I https://api.cg4f.online
curl -I https://cdn.cg4f.online

# Verify SSL certificate
openssl s_client -connect cg4f.online:443 -servername cg4f.online
```

### 4.3 Security Headers
```bash
# Check security headers
curl -I https://cg4f.online | grep -i "strict\|content\|frame\|xss"
```

## 5. Monitoring Setup

### 5.1 Health Checks
1. In CIS dashboard, go to Reliability > Health Checks
2. Create checks for:
   ```
   - Main domain (cg4f.online)
   - API endpoint (api.cg4f.online)
   - CDN (cdn.cg4f.online)
   ```
3. Configure:
   - Check interval: 60 seconds
   - Retries: 2
   - Timeout: 5 seconds

### 5.2 Analytics
1. Enable CIS Analytics
2. Configure log retention: 30 days
3. Set up email alerts for:
   - SSL certificate expiration
   - DNS zone changes
   - Security events

## 6. Backup and Documentation

### 6.1 DNS Records Backup
```bash
# Export DNS records
ibmcloud dns records cg4f.online > dns_backup_$(date +%Y%m%d).txt

# Export zone file
ibmcloud dns zone-export cg4f.online > zone_backup_$(date +%Y%m%d).txt
```

### 6.2 Regular Maintenance
- Weekly security scan
- Monthly SSL certificate check
- Quarterly security rules review
- Regular backup verification

## 7. Troubleshooting

### 7.1 Common Issues
1. DNS not resolving:
   - Verify DNS records in IBM Cloud console
   - Check for conflicting records
   - Clear local DNS cache

2. SSL Certificate issues:
   - Verify domain control
   - Check CAA records
   - Review SSL configuration in CIS

3. Performance issues:
   - Check CIS Analytics
   - Review cache settings
   - Monitor rate limiting

### 7.2 Support Contacts
- IBM Cloud Support: https://cloud.ibm.com/unifiedsupport/supportcenter
- CIS Documentation: https://cloud.ibm.com/docs/cis
- DNS Services Docs: https://cloud.ibm.com/docs/dns-svcs
