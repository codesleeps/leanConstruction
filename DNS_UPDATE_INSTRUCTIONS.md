# DNS Record Update Instructions for leanaiconstruction.com

## Overview
To make your Lean AI Construction platform accessible via your domain name, you need to update the DNS records to point to your VPS:
- `leanaiconstruction.com` → `72.61.16.111`
- `www.leanaiconstruction.com` → `72.61.16.111`

## Current Status
- **VPS IP Address**: `72.61.16.111`
- **VPS Hostname**: `srv1187860.hstgr.cloud`
- **Current DNS Resolution**: `84.32.84.32` (INCORRECT - needs to be updated)
- **Required DNS Resolution**: `72.61.16.111`

## URGENT: DNS Update Required

The DNS A records for `leanaiconstruction.com` are currently pointing to `84.32.84.32` instead of the VPS IP `72.61.16.111`. This must be corrected before SSL certificates can be installed.

## General DNS Update Process

1. **Log in to your domain registrar's control panel**
2. **Find the DNS management section** (often called "DNS Zone Editor", "DNS Management", or "Advanced DNS")
3. **Add or update the following records**:
   
   ### For leanaiconstruction.com:
   | Type | Name/Host | Value/Data    | TTL  |
   |------|-----------|---------------|------|
   | A    | @         | 72.61.16.111  | 300  |
   | A    | www       | 72.61.16.111  | 300  |

4. **Save the changes**
5. **Wait for DNS propagation** (can take anywhere from a few minutes to 48 hours)

## Registrar-Specific Instructions

### Hostinger DNS Update Instructions
1. Log in to your Hostinger account
2. Go to the "Hosting" section and select your domain
3. Click on "Manage" next to your domain name
4. Select "DNS Zone" from the menu
5. Click "Add Record" or edit existing A records
6. Update the following A records:
   - **Record Type**: A
   - **Hostname**: @ (for the main domain)
   - **Value**: `72.61.16.111`
   - **TTL**: 300
7. Add another A record:
   - **Record Type**: A
   - **Hostname**: www
   - **Value**: `72.61.16.111`
   - **TTL**: 300
8. Click "Save Changes"

### GoDaddy
1. Log in to your GoDaddy account
2. Navigate to "My Products" > "Domains"
3. Select your domain and click "DNS"
4. Under "Records", update or add the A records:
   - Type: A, Name: @, Value: `72.61.16.111`, TTL: 300
   - Type: A, Name: www, Value: `72.61.16.111`, TTL: 300
5. Click "Save"

### Namecheap
1. Log in to your Namecheap account
2. Go to "Domain List" and click "Manage" next to your domain
3. Select the "Advanced DNS" tab
4. Update or add the A records as shown in the table above
5. Click the green checkmark to save

### Google Domains
1. Log in to Google Domains
2. Select your domain
3. Click "DNS" in the left menu
4. Scroll down to "Custom resource records"
5. Update or add the A records as shown in the table above
6. Click "Add" to save each record

### Cloudflare
1. Log in to Cloudflare
2. Select your domain
3. Go to the "DNS" tab
4. Update or add the A records as shown in the table above
5. Make sure the cloud icon is gray (DNS only) for these records initially
6. Click "Save"

## Verification Commands

After updating DNS records, you can verify they're set correctly using:

### On macOS/Linux:
```bash
dig leanaiconstruction.com A +short
dig www.leanaiconstruction.com A +short
```

Expected output: `72.61.16.111`

### On Windows:
```cmd
nslookup leanaiconstruction.com
nslookup www.leanaiconstruction.com
```

You should see the response pointing to `72.61.16.111`.

### Online DNS Checker:
```bash
# Check DNS propagation status
./check-dns-propagation.sh
```

## DNS Propagation Time

DNS changes can take:
- **Immediate to 2 hours** - With low TTL values (as recommended above)
- **Up to 48 hours** - In some cases with higher TTL values or cached records

You can check propagation status using online tools like:
- https://whatsmydns.net
- https://dnschecker.org

## Troubleshooting

If your domains aren't resolving after 48 hours:
1. Double-check the DNS records in your registrar's control panel
2. Verify there are no typos in the domain names or IP address
3. Contact your domain registrar's support team
4. Check if there are any DNSSEC issues that might be blocking propagation

## Next Steps

After DNS propagation is complete (when `dig leanaiconstruction.com A +short` returns `72.61.16.111`):

1. **Install SSL certificate using Let's Encrypt**:
   ```bash
   ssh -i ~/.ssh/vps_deploy_key root@srv1187860.hstgr.cloud
   certbot --nginx -d leanaiconstruction.com -d www.leanaiconstruction.com
   ```

2. **Test access to your application**:
   - https://leanaiconstruction.com
   - https://www.leanaiconstruction.com

## Summary of Required Changes

| Domain | Current IP | Required IP | Action |
|--------|------------|-------------|--------|
| leanaiconstruction.com | 84.32.84.32 | 72.61.16.111 | UPDATE A RECORD |
| www.leanaiconstruction.com | 84.32.84.32 | 72.61.16.111 | UPDATE A RECORD |