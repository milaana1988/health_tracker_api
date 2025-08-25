# Theoretical Questions & Answers

## 1) Deployment on AWS

If I had to put this Health Tracker app on AWS, I’d probably start simple and then evolve it as traffic grows.

**Compute:** I’d containerize the FastAPI app with Docker. Then either run it on **ECS Fargate** (so AWS runs containers for me, no servers to manage), or on **Lambda + API Gateway** if I want serverless. ECS feels more “web-app” friendly because it’s always warm, while Lambda has cold-start issues.

**Database:** locally we used SQLite, but for production I’d switch to **RDS (Postgres)** or **Aurora Postgres**. That gives me backups, scaling, and failover out of the box.

**Authentication:** I’d plug in **Cognito** for user signup/login and JWT tokens. That way we don’t reinvent authentication, and it integrates nicely with API Gateway or even directly in the app.

**Secrets:** DB passwords, API keys → store in **Secrets Manager** or **SSM Parameter Store**, not in `.env`.

**Networking:** throw it behind an **Application Load Balancer** in a VPC, with ECS tasks in private subnets, DB also in private subnet.

**Storage/other:** use **S3** if I need to keep any files long term, **CloudWatch** for logs and metrics.

So the mental picture:  
Dockerized app → ECS Fargate tasks → ALB → internet.  
App talks to RDS in a private subnet. Auth handled by Cognito.

---

## 2) Scaling & Troubleshooting

Now imagine we suddenly have thousands of users per day and stuff starts breaking.

**Symptoms:**
- Health scores look wrong  
- API is slow  
- App sometimes crashes

### Step 1: Debug the accuracy
- Log what inputs go into the health score function. Sometimes the “inaccuracy” is just a **timezone bug** (UTC vs local day boundaries).
- Check normalization (min‑max across all users). If a few users have **wild outliers**, clamp or winsorize before normalizing.

### Step 2: Debug the slowness
- Slow APIs usually mean **database queries** are doing too much. Use **RDS Performance Insights** to spot missing indexes.
  - Add indexes on: `user_id`, `start_time`, `measured_at`.
- If health scores are recalculated on every request, **cache** them with **ElastiCache (Redis)**. Precompute periodically and serve from cache.

### Step 3: Debug the crashes
- Could be insufficient capacity → scale ECS service to multiple tasks (auto‑scaling on CPU/memory/latency).
- Could be leaks → run multiple gunicorn/uvicorn workers and set `max-requests` to recycle.
- Add **rate limiting** to protect under spikes.

---

## 3) Long‑term plan for resilience

- **Split responsibilities**:
  - Ingestion service (activity/sleep/blood).
  - Background worker service (score computation).
  - Public API service (serves results fast).
- **Queues:** Put heavy recomputes on **SQS** (or SNS→SQS). Workers consume asynchronously.
- **Precompute:** Store scores in a table; update on schedule or on new data events.
- **Monitoring:** CloudWatch (or Datadog) dashboards for latency, error rates, DB load; alerts on thresholds.
- **CI/CD:** Build → test → deploy via GitHub Actions to ECS/ECR. Use blue/green or canary deployments.

---

## 4) Bonus — Mapping User → FHIR Patient

**Internal `User`:** `id`, `email`, `full_name`, `gender`, `date_of_birth`, `height_cm`, `weight_kg`  
**FHIR `Patient`:** identifiers, name (given/family), gender, birthDate, etc.

**Mapping:**
- `User.id` → `Patient.identifier` (system = `health-tracker:user-id`)
- `full_name` → `Patient.name[0].text` (or split into given/family if possible)
- `gender` → `Patient.gender`
- `date_of_birth` → `Patient.birthDate`
- Height/weight are not Patient fields → publish as separate `Observation` resources (use proper **LOINC** codes)

**Challenges:**
- **Code systems**: LOINC/SNOMED and units must be correct.
- **Names**: may not split cleanly into given/family across locales.
- **Missing data**: unknown DOB/gender; represent with FHIR‑valid values like `unknown`.
- **Profiles/validation**: Interop means validating against specific FHIR profiles, not just the base spec.
