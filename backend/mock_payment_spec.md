# Mock Payment Endpoint

## Endpoint
```
POST /api/payment/mock
```

## Request Body
```json
{
  "user_id": "string",
  "amount": 20,
  "purpose": "call_payment"
}
```

## Response (Always Success)
```json
{
  "success": true,
  "message": "Mock payment successful",
  "transaction_id": "mock_txn_uuid",
  "amount": 20,
  "timestamp": "ISO_DATE"
}
```

## Implementation
- No wallet checks
- Always returns success
- Generates mock transaction ID
- Suitable for demo/testing
