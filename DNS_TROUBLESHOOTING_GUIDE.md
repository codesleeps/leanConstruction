# Website Accessibility Troubleshooting Guide

## Issue Identified
Your websites are not accessible because DNS resolution is failing. This means that when someone tries to visit constructionaipro.com or agentsflowai.cloud, the domain names are not being translated to your VPS IP address (srv1187860.hstgr.cloud).

## Possible Causes and Solutions

### 1. DNS Propagation Delay
**Cause**: DNS changes can take time to propagate across the internet.
**Solution**: 
- Wait for DNS propagation (can take up to 48 hours)
- Check propagation status at https://www.whatsmydns.net/

### 2. Incorrect DNS Records
**Cause**: The DNS records may not be configured correctly.
**Solution**:
- Log in to your Hostinger account
- Go to the DNS management section for both domains
- Verify that you have A records pointing to srv1187860.hstgr.cloud:
  - constructionaipro.com → srv1187860.hstgr.cloud
  - www.constructionaipro.com → srv1187860.hstgr.cloud
  - agentsflowai.cloud → srv1187860.hstgr.cloud
  - www.agentsflowai.cloud → srv1187860.hstgr.cloud

### 3. DNS Record Format Issues
**Cause**: DNS records may have been entered incorrectly.
**Solution**:
- Ensure you're using the correct record type (A record)
- Ensure there are no extra spaces or characters
- Ensure TTL is set to a reasonable value (300 seconds recommended)

### 4. Domain Registrar Issues
**Cause**: There might be issues with your domain registration or nameserver configuration.
**Solution**:
- Verify that your domains are using the correct nameservers
- Check that your domains are not expired
- Contact Hostinger support if you suspect an account issue

## Immediate Steps to Take

1. **Verify DNS Records in Hostinger**:
   - Log in to your Hostinger account
   - Navigate to the DNS management section for each domain
   - Confirm that A records exist for @ and www pointing to srv1187860.hstgr.cloud

2. **Check Nameservers**:
   - Ensure your domains are using Hostinger's nameservers
   - Typical Hostinger nameservers:
     - ns1.hostinger.com
     - ns2.hostinger.com
     - ns3.hostinger.com
     - ns4.hostinger.com

3. **Test Direct IP Access**:
   - Try accessing your VPS directly via its IP address
   - If this works, it confirms that your services are running but DNS is the issue

4. **Monitor DNS Propagation**:
   - Use tools like https://www.whatsmydns.net/ to check propagation status
   - Check from multiple locations/geographies

## If DNS Is Correct But Still Not Working

1. **Restart DNS Services**:
   ```bash
   sudo systemctl restart named  # If using BIND
   # or
   sudo systemctl restart pdns  # If using PowerDNS
   ```

2. **Clear Local DNS Cache**:
   - Windows: `ipconfig /flushdns`
   - macOS: `sudo dscacheutil -flushcache`
   - Linux: `sudo systemctl restart systemd-resolved`

3. **Check Firewall Settings**:
   ```bash
   sudo ufw status
   # Ensure ports 80 and 443 are allowed
   ```

## Emergency Access

If you need immediate access to your applications while DNS propagates:
1. Add entries to your local hosts file:
   - Windows: `C:\Windows\System32\drivers\etc\hosts`
   - macOS/Linux: `/etc/hosts`
   - Add lines:
     ```
     72.61.16.111 constructionaipro.com
     72.61.16.111 www.constructionaipro.com
     72.61.16.111 agentsflowai.cloud
     72.61.16.111 www.agentsflowai.cloud
     ```

## Contact Support

If you've verified all the above and are still experiencing issues:
1. Contact Hostinger support with:
   - Your domain names
   - The DNS records you've configured
   - Screenshots of your DNS settings
   - Results from the diagnostic script

2. Contact your VPS provider if you suspect network issues on their end.

## Next Steps

Once DNS is resolving correctly:
1. Proceed with SSL certificate installation using Let's Encrypt
2. Test website accessibility via both HTTP and HTTPS
3. Monitor site performance and fix any remaining issues