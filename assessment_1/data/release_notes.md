# Release Notes — Smart Insights v2.4.0

## Release Date: March 31, 2026

## Feature Overview

**Smart Insights** is PurpleMerit's new AI-powered analytics dashboard that provides users with:
- Real-time project performance metrics and visualizations
- AI-driven anomaly detection and automated alerts
- Predictive analytics for project timelines and resource allocation
- Competitive benchmarking (Pro tier)
- Custom report builder with CSV/PDF export
- Weekly automated email summaries

## Target Audience
- Small-to-medium business owners and project managers on all plans
- Smart Insights Pro features available as an add-on ($12/month)

## Technical Changes
- New microservice: `insights-engine` deployed on Kubernetes cluster
- Added 3 new API endpoints: `/api/v2/insights`, `/api/v2/insights/export`, `/api/v2/insights/alerts`
- Integrated TensorFlow Lite model for on-device prediction (mobile)
- Database migration: added 4 new tables (`insights_cache`, `user_preferences`, `alert_rules`, `report_templates`)
- Updated payment gateway integration for Smart Insights Pro subscriptions

## Known Issues

1. **Performance Degradation Under Load** (Severity: High)
   - The `insights-engine` microservice shows elevated p95 latency when concurrent users exceed 500
   - Root cause: N+1 query pattern in the dashboard aggregation pipeline
   - Mitigation: Query optimization planned for v2.4.1 (ETA: April 8)

2. **Mobile Crash on Older Devices** (Severity: Medium)
   - TensorFlow Lite model causes OOM crashes on devices with less than 4GB RAM
   - Affected: ~12% of mobile userbase
   - Mitigation: Fallback to server-side prediction for low-memory devices (in progress)

3. **Payment Gateway Timeout** (Severity: Medium)
   - Intermittent timeout errors (error code PM-4021) on Pro subscription checkout
   - Related to new payment flow not properly handling 3D Secure callbacks
   - Mitigation: Payment team investigating, hotfix targeted for April 5

4. **PDF Export Failure** (Severity: Low)
   - Custom date range exports occasionally fail with a rendering error
   - Affects approximately 5% of export attempts
   - Mitigation: Using fallback renderer; permanent fix in v2.4.1

## Rollout Plan
- Phase 1 (March 31): 10% canary rollout
- Phase 2 (April 1): 50% rollout if canary metrics stable
- Phase 3 (April 3): 100% rollout
- Decision checkpoint: April 6 war room to evaluate proceed/pause/rollback

## Success Criteria
- Signup conversion rate: no more than 5% degradation vs. baseline
- Crash rate: must remain below 1.0%
- API latency (p95): must remain below 300ms
- Payment success rate: must remain above 99.0%
- D1 retention: no more than 3pp drop vs. baseline
- Support ticket volume: no more than 30% increase vs. baseline
- Feature adoption funnel completion: >15% of DAU within 7 days

## Stakeholders
- **Product**: Sarah Chen (VP Product)
- **Engineering**: Marcus Williams (Engineering Lead)
- **Marketing**: Priya Patel (Head of Marketing)
- **Customer Success**: James Rodriguez (CS Director)
- **Risk/Compliance**: Aisha Okafor (Risk Manager)
