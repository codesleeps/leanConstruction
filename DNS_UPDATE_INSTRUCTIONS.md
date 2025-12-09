# DNS Record Update Instructions

## Overview
To make your applications accessible via your domain names, you need to update the DNS records to point to your VPS:
- `constructionaipro.com` → `srv1187860.hstgr.cloud`
- `agentsflowai.cloud` → `srv1187860.hstgr.cloud`

## General DNS Update Process

1. **Log in to your domain registrar's control panel**
2. **Find the DNS management section** (often called "DNS Zone Editor", "DNS Management", or "Advanced DNS")
3. **Add or update the following records**:
   
   ### For constructionaipro.com:
   | Type | Name/Host | Value/Data                  | TTL  |
   |------|-----------|-----------------------------|------|
   | A    | @         | srv1187860.hstgr.cloud      | 300  |
   | A    | www       | srv1187860.hstgr.cloud      | 300  |

   ### For agentsflowai.cloud:
   | Type | Name/Host | Value/Data                  | TTL  |
   |------|-----------|-----------------------------|------|
   | A    | @         | srv1187860.hstgr.cloud      | 300  |
   | A    | www       | srv1187860.hstgr.cloud      | 300  |

4. **Save the changes**
5. **Wait for DNS propagation** (can take anywhere from a few minutes to 48 hours)

## Registrar-Specific Instructions

### Hostinger DNS Update Instructions
1. Log in to your Hostinger account
2. Go to the "Hosting" section and select your domain
3. Click on "Manage" next to your domain name
4. Select "DNS Zone" from the menu
5. Click "Add Record"
6. Add the following A records:
   - **Record Type**: A
   - **Hostname**: @ (for the main domain) or www (for www subdomain)
   - **Value**: srv1187860.hstgr.cloud
   - **TTL**: 300
7. Repeat for both domains and both @ and www records
8. Click "Save Changes"

### GoDaddy
1. Log in to your GoDaddy account
2. Navigate to "My Products" > "Domains"
3. Select your domain and click "DNS"
4. Under "Records", add the A records as shown in the table above
5. Click "Save"

### Namecheap
1. Log in to your Namecheap account
2. Go to "Domain List" and click "Manage" next to your domain
3. Select the "Advanced DNS" tab
4. Add the A records as shown in the table above
5. Click the green checkmark to save

### Google Domains
1. Log in to Google Domains
2. Select your domain
3. Click "DNS" in the left menu
4. Scroll down to "Custom resource records"
5. Add the A records as shown in the table above
6. Click "Add" to save each record

### Cloudflare
1. Log in to Cloudflare
2. Select your domain
3. Go to the "DNS" tab
4. Add the A records as shown in the table above
5. Make sure the cloud icon is gray (DNS only) for these records
6. Click "Save"

## Verification Commands

After updating DNS records, you can verify they're set correctly using:

### On macOS/Linux:
```bash
dig constructionaipro.com
dig www.constructionaipro.com
dig agentsflowai.cloud
dig www.agentsflowai.cloud
```

### On Windows:
```cmd
nslookup constructionaipro.com
nslookup www.constructionaipro.com
nslookup agentsflowai.cloud
nslookup www.agentsflowai.cloud
```

You should see the response pointing to `srv1187860.hstgr.cloud` or its IP address.

## DNS Propagation Time

DNS changes can take:
- **Immediate to 2 hours** - With low TTL values (as recommended above)
- **Up to 48 hours** - In some cases with higher TTL values or cached records

You can check propagation status using online tools like:
- whatsmydns.net
- dnschecker.org

## Troubleshooting

If your domains aren't resolving after 48 hours:
1. Double-check the DNS records in your registrar's control panel
2. Verify there are no typos in the domain names or VPS hostname
3. Contact your domain registrar's support team
4. Check if there are any DNSSEC issues that might be blocking propagation

## Next Steps

After DNS propagation is complete:
1. Proceed with SSL certificate setup using Let's Encrypt
2. Test access to your applications via:
   - https://constructionaipro.com
   - https://agentsflowai.cloud