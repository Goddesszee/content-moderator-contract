A# content-moderator-contract

AI-powered content moderation smart contract built on [GenLayer](https://genlayer.com) — a blockchain that lets smart contracts run LLM inference natively. This contract submits user content for review, classifies it via an AI prompt, and stores the verdict, severity score, and reasoning on-chain.

---

## Overview

| Feature | Detail |
|---|---|
| Platform | GenLayer blockchain |
| Language | Python (GenLayer SDK) |
| Version | v0.2.16 |
| Verdicts | `APPROVED` · `REJECTED` · `REVIEW` |
| Severity scale | 0 (safe) → 10 (extremely harmful) |

---

## Contract state

| Variable | Type | Description |
|---|---|---|
| `next_id` | `u256` | Auto-incrementing content ID counter |
| `total_moderated` | `u256` | Count of fully moderated items |
| `contents` | `TreeMap[u256, str]` | Raw submitted content |
| `submitters` | `TreeMap[u256, str]` | Submitter wallet addresses |
| `categories` | `TreeMap[u256, str]` | Content category labels |
| `statuses` | `TreeMap[u256, str]` | Lifecycle status per item |
| `verdicts` | `TreeMap[u256, str]` | AI verdict per item |
| `reasonings` | `TreeMap[u256, str]` | AI reasoning explanation |
| `severity_scores` | `TreeMap[u256, str]` | Numeric severity 0–10 |

---

## Methods

### `submit_content(content: str, category: str) → int`

Submits content for moderation. Returns the assigned `content_id`.

- Content must be at least 5 characters
- Status is set to `"pending"` on submission
- `category` is a free-form label (e.g. `"social_media"`, `"comment"`, `"forum_post"`)

```python
contract.submit_content("This is a test post.", "forum_post")
# returns: 1
```

---

### `moderate(content_id: u256) → dict`

Triggers AI moderation for a pending item. Uses `gl.nondet.exec_prompt` to call an LLM and `gl.eq_principle.strict_eq` to reach consensus across validators.

- Content must have status `"pending"`
- Status transitions: `pending` → `reviewing` → `moderated`
- Returns the full moderation result as a dict

```python
contract.moderate(1)
# returns:
# {
#   "verdict": "APPROVED",
#   "severity_score": 0,
#   "violations": [],
#   "reasoning": "The content is respectful and follows community guidelines."
# }
```

**Violation categories checked:**
- Hate speech or discrimination
- Violence or threats
- Sexual or explicit content
- Harassment or bullying
- Spam or scam content
- Misinformation
- Illegal activity promotion

---

### `get_content(content_id: u256) → dict`

Returns the full record for a given content ID.

```python
contract.get_content(1)
# returns:
# {
#   "id": 1,
#   "content": "This is a test post.",
#   "category": "forum_post",
#   "submitter": "0xabc...",
#   "status": "moderated",
#   "verdict": "APPROVED",
#   "severity_score": "0",
#   "reasoning": "Content is safe and respectful."
# }
```

---

### `get_stats() → dict`

Returns aggregate contract statistics.

```python
contract.get_stats()
# returns:
# {
#   "total_submitted": 5,
#   "total_moderated": 3
# }
```

---

## Content lifecycle

```
submit_content()
      │
      ▼
   pending
      │
  moderate()
      │
      ▼
  reviewing  ──(LLM inference + validator consensus)──▶  moderated
```

---

## Verdict reference

| Verdict | Meaning |
|---|---|
| `APPROVED` | Content is safe and follows community guidelines |
| `REJECTED` | Content contains hate speech, violence, explicit material, harassment, spam, or illegal content |
| `REVIEW` | Borderline or ambiguous — flagged for human review |

---

## Getting started

### Prerequisites

- [GenLayer Studio](https://studio.genlayer.com) account, or a local GenLayer node
- Python 3.10+
- GenLayer SDK: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

### Deploy

1. Clone this repo:
   ```bash
   git clone https://github.com/Goddesszee/content-moderator-contract.git
   cd content-moderator-contract
   ```

2. Open `content_moderator.py` in GenLayer Studio and deploy to the testnet.

3. Copy the deployed contract address for use in your frontend or scripts.

---

## Example interaction

```python
# 1. Submit content
id = contract.submit_content("Buy cheap watches now!! Click here.", "comment")

# 2. Run moderation
result = contract.moderate(id)
print(result["verdict"])        # "REJECTED"
print(result["severity_score"]) # 7
print(result["violations"])     # ["Spam or scam content"]

# 3. Retrieve the record
record = contract.get_content(id)
print(record["status"])         # "moderated"
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
