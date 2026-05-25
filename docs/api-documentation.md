# API Documentation

Base URL (dev): `http://localhost:8000/api/v1`

Every response follows the same envelope:

```json
{
  "success": true,
  "message": "OK",
  "data": { ... }
}
```

When `success` is `false`, `message` describes the error and
`data.errors` (if present) lists the offending fields.

---

## 1. List feedback

`GET /feedback`

**Query parameters**

| Name        | Type | Default | Description                |
| ----------- | ---- | ------- | -------------------------- |
| `page`      | int  | 1       | Page number (>= 1).        |
| `page_size` | int  | 20      | Items per page (1–100).    |

**Response 200**

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "total": 42,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "feedback_id": 1,
        "participant_name": "Jane Doe",
        "program_name": "AI Bootcamp 2026",
        "rating": 5,
        "rating_label": "Excellent",
        "comments": "Outstanding mentors and content.",
        "submitted_at": "2026-05-13T10:14:32"
      }
    ]
  }
}
```

---

## 2. Get feedback by ID

`GET /feedback/{feedback_id}`

**Response 200**

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "feedback_id": 1,
    "participant_name": "Jane Doe",
    "program_name": "AI Bootcamp 2026",
    "rating": 5,
    "rating_label": "Excellent",
    "comments": "Outstanding mentors and content.",
    "submitted_at": "2026-05-13T10:14:32"
  }
}
```

**Response 404**

```json
{
  "success": false,
  "message": "Feedback with id=999 was not found.",
  "data": null
}
```

---

## 3. Create feedback

`POST /feedback`

**Request body**

```json
{
  "participant_name": "Jane Doe",
  "program_name": "AI Bootcamp 2026",
  "rating": 5,
  "comments": "Outstanding mentors and content."
}
```

**Response 201**

```json
{
  "success": true,
  "message": "Feedback submitted successfully.",
  "data": {
    "feedback_id": 1,
    "participant_name": "Jane Doe",
    "program_name": "AI Bootcamp 2026",
    "rating": 5,
    "rating_label": "Excellent",
    "comments": "Outstanding mentors and content.",
    "submitted_at": "2026-05-13T10:14:32"
  }
}
```

---

## 4. Update feedback (partial)

`PUT /feedback/{feedback_id}`

Provide one or more fields.

**Request body**

```json
{
  "rating": 4,
  "comments": "Updated after the closing session."
}
```

**Response 200**

```json
{
  "success": true,
  "message": "Feedback updated successfully.",
  "data": { /* updated FeedbackResponse */ }
}
```

If no fields are supplied:

```json
{
  "success": false,
  "message": "At least one field must be provided for an update.",
  "data": null
}
```

---

## 5. Delete feedback

`DELETE /feedback/{feedback_id}`

**Response 200**

```json
{
  "success": true,
  "message": "Feedback deleted successfully.",
  "data": null
}
```

---

## 6. Search and filter

`GET /feedback/search`

| Query param    | Type | Description                                                |
| -------------- | ---- | ---------------------------------------------------------- |
| `keyword`      | str  | Partial, case-insensitive match on name / program / comments. |
| `rating`       | int  | Exact rating filter (1–5).                                 |
| `program_name` | str  | Partial program name match.                                |
| `page`         | int  | Page (>= 1).                                               |
| `page_size`    | int  | Items per page (1–100).                                    |

Combine any of `keyword`, `rating`, `program_name`. All are optional.

Example:

```
GET /feedback/search?keyword=mentor&rating=5&page=1&page_size=10
```

Response is identical in shape to **List feedback**.

---

## 7. Dashboard statistics

`GET /feedback/stats`

| Query param    | Type | Default | Description                       |
| -------------- | ---- | ------- | --------------------------------- |
| `recent_limit` | int  | 5       | How many recent items to return.  |

**Response 200**

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "total_feedback": 42,
    "average_rating": 4.21,
    "rating_distribution": { "1": 1, "2": 2, "3": 5, "4": 12, "5": 22 },
    "recent_feedback": [ /* FeedbackResponse[] */ ]
  }
}
```

---

## Validation rules

| Field              | Rule                                                     |
| ------------------ | -------------------------------------------------------- |
| `participant_name` | required; 2–120 characters; whitespace trimmed.          |
| `program_name`     | required; 2–150 characters; whitespace trimmed.          |
| `rating`           | required integer in `[1, 5]`.                            |
| `comments`         | required; 3–2000 characters; whitespace trimmed.         |

All validation errors return HTTP `422` with `success: false`.

## HTTP status codes

| Code | When                                          |
| ---- | --------------------------------------------- |
| 200  | Successful GET / PUT / DELETE.                |
| 201  | Feedback created.                             |
| 400  | Update payload had no fields.                 |
| 404  | Feedback id not found.                        |
| 422  | Request body / query failed validation.       |
| 500  | Unhandled / database error.                   |
