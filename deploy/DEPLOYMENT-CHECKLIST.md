# EVA RAG - Deployment Checklist

Use this checklist to ensure all steps are completed for a successful deployment.

## 🎯 Pre-Deployment (T-48 hours)

### Code Preparation
- [ ] All tests passing locally (`poetry run pytest`)
- [ ] Code coverage meets target (>97%)
- [ ] Security scan clean (`poetry run bandit -r src/`)
- [ ] Dependencies up to date (`poetry update`)
- [ ] No secrets in repository (check `.gitignore`)
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG updated with new features/fixes

### Documentation
- [ ] README.md is current
- [ ] API documentation reviewed
- [ ] Deployment guide reviewed
- [ ] Known issues documented
- [ ] Rollback plan documented

### Infrastructure
- [ ] Azure resources provisioned
- [ ] DNS configured (if applicable)
- [ ] SSL certificates valid
- [ ] Firewall rules configured
- [ ] Storage accounts created
- [ ] Cosmos DB configured
- [ ] Key Vault secrets populated

### Monitoring
- [ ] Application Insights configured
- [ ] Log Analytics workspace created
- [ ] Alert rules configured
- [ ] Dashboard created
- [ ] On-call rotation confirmed

## 📋 Pre-Deployment (T-24 hours)

### Environment Configuration
- [ ] `.env.example` file complete
- [ ] Environment variables documented
- [ ] Secrets stored in Key Vault
- [ ] Configuration validated in staging
- [ ] Feature flags configured

### Testing
- [ ] Unit tests passing (129/129)
- [ ] Integration tests passing
- [ ] Performance tests run
- [ ] Load testing completed
- [ ] Security testing done
- [ ] Accessibility testing (if applicable)

### Backup & Recovery
- [ ] Current production backed up
- [ ] Backup restoration tested
- [ ] Rollback plan tested
- [ ] Database migration scripts ready
- [ ] Disaster recovery plan reviewed

### Communication
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled
- [ ] Status page updated
- [ ] Support team briefed
- [ ] Runbook shared with team

## 🚀 Deployment (T-0)

### Pre-Deployment Checks
- [ ] All pre-deployment items complete
- [ ] Team on standby
- [ ] Monitoring dashboards open
- [ ] Communication channels ready
- [ ] Rollback decision criteria defined

### Deployment Execution

#### Staging Deployment
- [ ] Deploy to staging environment
  ```powershell
  .\deploy\deploy.ps1 -Environment staging
  ```
- [ ] Run smoke tests
- [ ] Verify health checks
- [ ] Test key workflows
- [ ] Performance validation
- [ ] Security validation

#### Production Deployment
- [ ] Final approval received
- [ ] Maintenance mode enabled (if applicable)
- [ ] Deploy to production
  ```powershell
  .\deploy\deploy.ps1 -Environment production
  ```
- [ ] Monitor deployment logs
- [ ] Watch error rates
- [ ] Check performance metrics

## ✅ Post-Deployment Validation (T+30 min)

### Health Checks
- [ ] Application health endpoint responding
  ```powershell
  Invoke-RestMethod https://eva-rag-prod.azurewebsites.net/health
  ```
- [ ] All dependencies healthy
- [ ] Database connections working
- [ ] Storage access working
- [ ] API responses normal

### Functional Testing
- [ ] Document upload working
- [ ] Document processing working
- [ ] Search functionality working
- [ ] Embeddings generation working
- [ ] Metadata CRUD working
- [ ] Authentication working (if applicable)

### Performance Validation
- [ ] Response times normal (<2s p95)
- [ ] CPU usage normal (<70%)
- [ ] Memory usage normal (<80%)
- [ ] No memory leaks
- [ ] Error rate acceptable (<0.1%)

### Monitoring
- [ ] Application Insights receiving data
- [ ] Logs flowing correctly
- [ ] Metrics being collected
- [ ] Alerts configured and working
- [ ] Dashboard showing data

## 🔍 Post-Deployment (T+2 hours)

### Stability Monitoring
- [ ] No critical errors in logs
- [ ] Performance metrics stable
- [ ] Error rates within SLOs
- [ ] User reports reviewed
- [ ] Support tickets reviewed

### Documentation
- [ ] Deployment notes documented
- [ ] Any issues logged
- [ ] Runbook updated
- [ ] Known issues updated
- [ ] Status page updated

### Communication
- [ ] Deployment success announced
- [ ] Known issues communicated
- [ ] Documentation links shared
- [ ] Support team updated
- [ ] Stakeholders notified

## 📊 Post-Deployment (T+24 hours)

### Health Review
- [ ] 24-hour metrics reviewed
- [ ] Error patterns analyzed
- [ ] Performance trends reviewed
- [ ] User feedback collected
- [ ] Support tickets analyzed

### Post-Mortem (if issues)
- [ ] Timeline documented
- [ ] Root cause identified
- [ ] Action items created
- [ ] Lessons learned documented
- [ ] Process improvements identified

## 🚨 Rollback Procedure (If Needed)

### Decision Criteria
Rollback if any of the following occur:
- [ ] Critical functionality broken
- [ ] Error rate > 5%
- [ ] Response time > 5s p95
- [ ] Data corruption detected
- [ ] Security vulnerability discovered

### Rollback Steps
1. **Immediate Actions**
   - [ ] Announce rollback decision
   - [ ] Stop new deployments
   - [ ] Document reason for rollback

2. **Execute Rollback**
   ```powershell
   # Azure App Service slot swap
   az webapp deployment slot swap \
     --name eva-rag-prod \
     --resource-group eva-rag-prod \
     --slot staging
   
   # Or redeploy previous version
   git checkout <previous-commit>
   .\deploy\deploy.ps1 -Environment production
   ```

3. **Verify Rollback**
   - [ ] Health checks passing
   - [ ] Functionality restored
   - [ ] Metrics returning to normal
   - [ ] User reports improving

4. **Post-Rollback**
   - [ ] Incident report created
   - [ ] Root cause analysis scheduled
   - [ ] Fix plan created
   - [ ] Re-deployment planned

## 📝 Sign-Off

### Staging Deployment
- **Deployed by:** ___________________
- **Date/Time:** ___________________
- **Version:** ___________________
- **Status:** ⬜ Success  ⬜ Failed  ⬜ Rolled Back
- **Notes:** ___________________

### Production Deployment
- **Deployed by:** ___________________
- **Date/Time:** ___________________
- **Version:** ___________________
- **Status:** ⬜ Success  ⬜ Failed  ⬜ Rolled Back
- **Approved by:** ___________________
- **Notes:** ___________________

## 🎯 Success Criteria

Deployment is considered successful when:
- ✅ All health checks passing
- ✅ Error rate < 0.1%
- ✅ Response time p95 < 2s
- ✅ CPU usage < 70%
- ✅ Memory usage < 80%
- ✅ All functional tests passing
- ✅ No critical issues reported
- ✅ Stable for 24 hours

---

**Checklist Version:** 1.0  
**Last Updated:** December 8, 2025  
**Owner:** EVA Suite Operations Team
