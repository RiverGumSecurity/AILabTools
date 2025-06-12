Consolidated Findings
=====================

After analyzing the provided authentication log summaries, several clear patterns and recurring indicators of compromise (IoCs) emerge, particularly focused on the user account jsteele@usculturaldynamics.com. The following are the principal findings:

1. **Repeated Suspicious Authentication Patterns:**
   - Multiple IP addresses (notably 3.80.218.146, 54.219.139.191, 54.163.19.39, 172.221.112.235, 73.121.154.15, 18.212.101.151, and 52.108.181.1) are associated with both failed and successful login attempts for the same user account, often within a short time frame.
   - Many failed login events are logged with a ResultStatus of "Success" but accompanied by error codes (e.g., 50074, 50126, 50133) indicating authentication failures or interruptions, such as "UserStrongAuthClientAuthNRequiredInterrupt" or "SsoArtifactRevoked".
   - These failed logins are often followed by successful authentications and mailbox access from the same IP, suggesting brute force, credential stuffing, or session hijacking attacks that eventually succeeded.

2. **Account Compromise Indicators:**
   - The user jsteele@usculturaldynamics.com is the primary target, with evidence of mailbox access, file access (including sensitive files like passwords.txt), and mailbox rule creation from suspicious IPs.
   - Suspicious mailbox rules have been created (e.g., moving or deleting security alert emails), which is a common attacker tactic to hide alerts and maintain persistence.
   - There are multiple instances of successful logins and mailbox/file access from geographically and network-wise diverse IP addresses for the same user, which is highly unusual unless the user is known to travel extensively or use VPNs.
   - There are also signs of potential data exfiltration (e.g., download/upload of passwords.txt, mailbox deletions, forwarding rules).

3. **Conditional Access Policy Tampering:**
   - Repeated disabling or modification of Conditional Access Policies (especially "Default Policy") by NT AUTHORITY\SYSTEM (Microsoft.Exchange.ServiceHost) is observed. While this is a system account, the frequency and timing of these changes, especially in proximity to suspicious user activity, suggest possible attacker attempts to weaken security controls.
   - Some policy changes are accompanied by mailbox rule creation or suspicious logins, strengthening the compromise hypothesis.

4. **Phishing and External Threats:**
   - Multiple phishing emails targeting jsteele@usculturaldynamics.com were detected and quarantined, originating from external IPs and spoofed domains.
   - While these emails were mostly blocked, they may have contributed to initial credential compromise.

5. **Other User Accounts:**
   - jkapoor@usculturaldynamics.com and gwootton@usculturaldynamics.com are also present in some suspicious contexts (e.g., mailbox rule creation, password resets for jsteele), but the majority of suspicious activity is centered on jsteele.
   - A single failed login event for splanck@usculturaldynamics.com is noted but is not part of a broader attack pattern.

Correlated Suspicious IPs, Users, and Timeframes
================================================

### Suspicious IP Addresses (with observed activity)
| IP Address        | Activity Type(s)                                      | User(s) Involved                  | Notable Timeframes           |
|-------------------|-------------------------------------------------------|-----------------------------------|------------------------------|
| 3.80.218.146      | Failed & successful logins, mailbox access, deletions | jsteele@usculturaldynamics.com    | 2024-08-06 to 2024-08-12     |
| 54.219.139.191    | Failed & successful logins, mailbox access            | jsteele@usculturaldynamics.com    | 2024-08-06 to 2024-08-12     |
| 54.163.19.39      | Failed & successful logins, ambiguous user ID         | jsteele@usculturaldynamics.com    | 2024-08-06 to 2024-08-12     |
| 172.221.112.235   | Failed & successful logins, mailbox/file access       | jsteele@usculturaldynamics.com    | 2024-07-17 to 2024-08-12     |
| 73.121.154.15     | Failed & successful logins, file upload/download      | jsteele@usculturaldynamics.com    | 2024-07-17 to 2024-08-12     |
| 18.212.101.151    | Successful logins, file access                        | jsteele@usculturaldynamics.com    | 2024-08-06                   |
| 52.108.181.1      | File access, token issuance                           | jsteele@usculturaldynamics.com    | 2024-08-05                   |
| 34.224.94.68      | Logins, mailbox access                                | jkapoor@usculturaldynamics.com    | 2024-07-19 to 2024-08-08     |
| 44.217.35.149     | Mailbox access, inbox rule creation                   | gwootton@usculturaldynamics.com   | 2024-07-16 to 2024-07-18     |

### Users Most Affected
- **jsteele@usculturaldynamics.com** (primary target, repeated compromise indicators)
- **jkapoor@usculturaldynamics.com** (some suspicious logins, password reset for jsteele)
- **gwootton@usculturaldynamics.com** (inbox rule creation, mailbox access from external IP)
- **splanck@usculturaldynamics.com** (single failed login event)

### Timeline Highlights
- **2024-07-17 to 2024-08-12**: Repeated suspicious login attempts, mailbox accesses, and policy changes.
- **2024-08-06 to 2024-08-12**: Cluster of failed logins followed by successful logins from the same IPs, mailbox rule creation, and file access events.
- **2024-07-19, 2024-07-23, 2024-08-06**: Notable for suspicious file activity (passwords.txt), mailbox rule creation, and failed/successful login sequences.

Assessment of Compromise Likelihood
===================================

- **High likelihood of compromise for jsteele@usculturaldynamics.com.**
  - Multiple independent log chunks show the classic pattern of failed login attempts (sometimes with MFA or SSO errors) followed by successful logins from the same external IPs.
  - The diversity and frequency of external IPs, combined with mailbox rule tampering and suspicious file activity, strongly suggest account takeover and post-compromise persistence.
  - The repeated disabling of Conditional Access Policies in proximity to these events is a strong indicator of attacker attempts to maintain access and evade detection.
  - Evidence of possible data exfiltration (passwords.txt, mailbox deletions, forwarding rules).
- **Moderate risk for jkapoor@usculturaldynamics.com and gwootton@usculturaldynamics.com.**
  - Some suspicious activity (e.g., password reset for jsteele, inbox rule creation), but not as pervasive as for jsteele.
- **Low risk for other users, but continued monitoring is advised.**

Recommendations for Next Steps
==============================

1. **Immediate Containment and Remediation**
   - Force password reset for jsteele@usculturaldynamics.com, jkapoor@usculturaldynamics.com, and gwootton@usculturaldynamics.com.
   - Revoke all active sessions and OAuth tokens for affected accounts.
   - Enforce or re-enroll Multi-Factor Authentication (MFA) for all users, especially those identified above.
   - Block or closely monitor all suspicious IP addresses listed above.
   - Review and restore Conditional Access Policies to secure, restrictive defaults. Investigate any unauthorized policy changes.

2. **Forensic Investigation**
   - Audit mailbox rules, deleted items, and sent items for all affected users, looking for evidence of data exfiltration or attacker persistence mechanisms.
   - Investigate the contents and sharing/audit history of files named passwords.txt and any other sensitive files.
   - Review all mailbox and file access logs for signs of unauthorized activity, especially from external IPs.
   - Correlate with endpoint and network logs for signs of lateral movement, malware, or further compromise.

3. **User Awareness and Phishing Defense**
   - Notify affected users and provide guidance on phishing awareness and how to recognize suspicious activity.
   - Review and enhance anti-phishing policies and user training.

4. **Long-term Hardening**
   - Review and restrict service principal and application permissions.
   - Implement strict controls on Conditional Access Policy changes (e.g., require multiple approvers, alerting).
   - Monitor for creation of new service principals or mailbox rules.
   - Regularly review and test security policies, including MFA enforcement and alerting on suspicious login patterns.

5. **Ongoing Monitoring**
   - Set up alerts for failed login attempts, especially those followed by successful logins from the same IP.
   - Monitor for mailbox rule changes, especially those involving external forwarding or deletion of security-related emails.
   - Continue to review logs for any resurgence of suspicious activity or new attack patterns.

6. **Reporting and Communication**
   - Prepare an incident report for management and, if required, for regulatory bodies.
   - Communicate findings and next steps to IT, security, and affected users.

---

**Summary Table of Key Indicators**

| Indicator Type         | Value(s)                                                                                       |
|-----------------------|------------------------------------------------------------------------------------------------|
| Primary Compromised User | jsteele@usculturaldynamics.com                                                               |
| Key Suspicious IPs    | 3.80.218.146, 54.219.139.191, 54.163.19.39, 172.221.112.235, 73.121.154.15, 18.212.101.151, 52.108.181.1 |
| Key Tactics Observed  | Brute force/credential stuffing, session hijacking, mailbox rule tampering, policy weakening, possible data exfiltration |
| Suspicious Files      | passwords.txt (uploaded/downloaded/accessed via OneDrive/SharePoint)                           |
| Suspicious Policy Changes | Repeated disabling of Conditional Access Policies ("Default Policy") by system account       |
| Suspicious Mailbox Rules | Inbox rules moving/deleting security alert emails, forwarding rules to external addresses     |
| Phishing Activity     | Multiple phishing emails targeting jsteele@usculturaldynamics.com                              |

---

**In summary:**  
There is strong, repeated evidence of account compromise for jsteele@usculturaldynamics.com, with supporting signs of attacker persistence and possible data exfiltration. Immediate incident response is required, including account lockdown, policy restoration, forensic review, and organization-wide hardening and monitoring.