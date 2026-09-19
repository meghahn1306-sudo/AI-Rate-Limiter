# AI-Rate-Limiter
A FastAPI-based AI rate limiter that controls AI API usage using the Token Bucket algorithm.

## Overview

The AI Rate Limiter controls the amount of AI requests a user can make based on token consumption.

It helps prevent excessive API usage and provides controlled access to AI services.

The project calculates the estimated token cost of each request, checks the user's available tokens, and either processes or rejects the request.

## Features

* Token Bucket based rate limiting
* Per-user token tracking
* Token refill over time
* Estimated token cost calculation
* HTTP 429 response when the limit is exceeded
* Retry time information in the 429 response
* Request statistics
* Rate-limit status endpoint
* Health-check endpoint
* Swagger/OpenAPI API documentation
* FastAPI backend

## Technologies Used

* Python
* FastAPI
* Uvicorn
* Token Bucket Algorithm
* Swagger / OpenAPI

## Project Structure

```text
rate_limiter/
│
├── main.py
└── README.md
```

## How It Works

The system follows these steps:

```text
Client Request
      ↓
Read User ID
      ↓
Calculate Estimated Token Cost
      ↓
Check Token Bucket
      ↓
 ┌───────────────┐
 │ Enough Tokens?│
 └───────────────┘
      ↓       ↓
     YES      NO
      ↓       ↓
 Process    HTTP 429
 Request    Rate Limit
      ↓
 Deduct Tokens
      ↓
 Return Response
```

## Token Bucket

Each user has a token bucket.

Current configuration:

```python
BUCKET_MAX_TOKENS = 10
REFILL_RATE_PER_SECOND = 1
```

This means:

* Maximum bucket capacity = **10 tokens**
* Refill rate = **1 token per second**
* Each request consumes tokens based on the estimated prompt cost.

For example, a short request such as:

```json
{
  "prompt": "hello"
}
```

has an estimated cost of at least 1 token.

If sufficient tokens are available, the request is processed.

If insufficient tokens are available, the API returns:

**HTTP 429 — Too Many Requests**

## API Endpoints

### 1. Health Check

```text
GET /health
```

Checks whether the service is running.

Example response:

```json
{
  "status": "healthy",
  "service": "AI Rate Limiter"
}
```

### 2. Rate Limit Status

```text
GET /v1/rate-limit
```

Returns the current token information for a user.

Example:

```json
{
  "user_id": "anonymous_user",
  "available_tokens": 10,
  "maximum_tokens": 10,
  "refill_rate_per_second": 1
}
```

### 3. Statistics

```text
GET /v1/stats
```

Returns request statistics.

Example:

```json
{
  "total_users": 1,
  "total_requests": 5,
  "active_users": [
    "anonymous_user"
  ]
}
```

### 4. AI Request

```text
POST /v1/chat/completions
```

Example request:

```json
{
  "prompt": "hello"
}
```

Example successful response:

```json
{
  "status": "success",
  "estimated_tokens_used": 1,
  "remaining_tokens": 9,
  "remaining_time_ms": 0,
  "request_count": 1,
  "ai_response": "Response to: hello"
}
```

## Rate Limit Response

When the user does not have enough tokens, the API returns:

```text
429 Too Many Requests
```

Example:

```json
{
  "detail": {
    "message": "Rate limit exceeded",
    "user_id": "anonymous_user",
    "available_tokens": 0,
    "required_tokens": 1,
    "retry_after_seconds": 1.0
  }
}
```

The `retry_after_seconds` value tells the client approximately how long it needs to wait before enough tokens are available.

## Testing

The API was tested using **Swagger UI**.

The following tests were successfully performed:

* Health check → **200**
* Rate-limit status → **200**
* Statistics → **200**
* Successful AI request → **200**
* Rate limit exceeded → **429**

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Example Testing Flow

First request:

```text
200 OK
```

The request is processed and tokens are deducted.

After repeatedly sending requests:

```text
429 Too Many Requests
```

The request is rejected because the user's available tokens are insufficient.

After waiting for token refill, requests can be processed again.

## Advantages

* Prevents excessive AI API usage
* Controls token consumption
* Supports individual users
* Provides clear rate-limit information
* Easy to test through Swagger
* Simple FastAPI implementation
* Can be extended for production systems

## Future Improvements

The current project uses in-memory storage for simplicity.

Possible future improvements include:

* Redis-based token storage
* Persistent request statistics
* Multiple API keys
* Authentication
* Distributed rate limiting
* Multiple rate-limit policies
* Real AI model integration
* Monitoring dashboard
* Docker deployment
* Cloud deployment

## Conclusion

The AI Rate Limiter demonstrates how an AI service can control usage through the **Token Bucket rate-limiting algorithm**.

The system tracks user tokens, refills them over time, processes requests when sufficient tokens are available, and returns an HTTP 429 response when the limit is exceeded.

This project provides a foundation for building scalable and controlled AI APIs.

