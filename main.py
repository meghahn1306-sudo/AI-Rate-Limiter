from fastapi import FastAPI, Request, HTTPException, status, Header
import time

app = FastAPI(title="AI Rate Limiter")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Rate Limiter"
    }

@app.get("/v1/rate-limit")
def rate_limit_status(x_user_id: str = Header(default="anonymous_user")):

    user_id = x_user_id

    tokens, current_time = get_token_bucket(user_id)

    return {
        "user_id": user_id,
        "available_tokens": int(tokens),
        "maximum_tokens": BUCKET_MAX_TOKENS,
        "refill_rate_per_second": REFILL_RATE_PER_SECOND
    }

@app.get("/v1/stats")
def get_stats():

    total_users = len(request_counts)
    total_requests = sum(request_counts.values())

    return {
        "total_users": total_users,
        "total_requests": total_requests,
        "active_users": list(request_counts.keys())
    }

BUCKET_MAX_TOKENS = 10
REFILL_RATE_PER_SECOND = 1

buckets = {}
request_counts: dict[str, int] = {}


def get_token_bucket(user_id):
    current_time = time.time()

    if user_id not in buckets:
        buckets[user_id] = {
            "tokens": BUCKET_MAX_TOKENS,
            "last_update": current_time
        }

    bucket = buckets[user_id]

    elapsed_time = current_time - bucket["last_update"]

    tokens = min(
        BUCKET_MAX_TOKENS,
        bucket["tokens"] + elapsed_time * REFILL_RATE_PER_SECOND
    )

    return tokens, current_time


@app.post("/v1/chat/completions")
async def handle_ai_request(request: Request, body : dict, x_user_id: str = Header(default="anonymous_user")):

    start_time = time.time()

    user_id = x_user_id

    request_counts[user_id] = request_counts.get(user_id, 0) + 1

    prompt = body.get("prompt", "")

    estimated_cost = max(
        1,
        int(len(prompt) * 0.25)
    )

    tokens, current_time = get_token_bucket(user_id)

    if tokens < estimated_cost:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "message": "Rate limit exceeded",
            "user_id": user_id,
            "available_tokens": int(tokens),
            "required_tokens": estimated_cost,
            "retry_after_seconds": round(
                (estimated_cost - tokens) / REFILL_RATE_PER_SECOND,
                2
            )
        }
    )

    new_balance = tokens - estimated_cost

    buckets[user_id] = {
        "tokens": new_balance,
        "last_update": current_time
    }

    return {
        "status": "success",
        "estimated_tokens_used": estimated_cost,
        "remaining_tokens": int(new_balance),
        "remaining_time_ms":round((time.time()-start_time)*1000,2),
         "request_count": request_counts[user_id],
        "ai_response": f"Response to: {prompt}"
    }