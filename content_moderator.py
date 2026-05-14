# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import json
import typing


class ContentModerator(gl.Contract):

    next_id: u256
    total_moderated: u256
    contents: TreeMap[u256, str]
    submitters: TreeMap[u256, str]
    categories: TreeMap[u256, str]
    statuses: TreeMap[u256, str]
    verdicts: TreeMap[u256, str]
    reasonings: TreeMap[u256, str]
    severity_scores: TreeMap[u256, str]

    def __init__(self) -> None:
        self.next_id = u256(1)
        self.total_moderated = u256(0)

    @gl.public.write
    def submit_content(self, content: str, category: str) -> typing.Any:
        assert len(content) >= 5, "Content must be at least 5 characters"

        content_id = self.next_id
        self.next_id = u256(int(self.next_id) + 1)

        self.contents[content_id] = content
        self.categories[content_id] = category
        self.submitters[content_id] = gl.message.sender_address
        self.statuses[content_id] = "pending"
        self.verdicts[content_id] = ""
        self.reasonings[content_id] = ""
        self.severity_scores[content_id] = ""

        return int(content_id)

    @gl.public.write
    def moderate(self, content_id: u256) -> typing.Any:
        assert self.statuses[content_id] == "pending", "Content is not pending"

        content = self.contents[content_id]
        category = self.categories[content_id]

        self.statuses[content_id] = "reviewing"

        def get_verdict() -> typing.Any:
            prompt = f"""You are an AI content moderator on the GenLayer blockchain.

CONTENT CATEGORY: {category}

CONTENT SUBMITTED FOR REVIEW:
"{content}"

Your job is to moderate this content based on standard community guidelines.

Rules:
- APPROVED = content is safe, respectful, and follows community guidelines
- REJECTED = content contains hate speech, violence, explicit material, harassment, spam, or illegal content
- REVIEW = content is borderline, ambiguous, or needs human review

Severity Score: 0-10 (0 = completely safe, 10 = extremely harmful)

Violations to check for:
- Hate speech or discrimination
- Violence or threats
- Sexual or explicit content
- Harassment or bullying
- Spam or scam content
- Misinformation
- Illegal activity promotion

Respond with this JSON format:
{{
    "verdict": "APPROVED" or "REJECTED" or "REVIEW",
    "severity_score": 0-10,
    "violations": ["list of violations found, empty if none"],
    "reasoning": "your 2-3 sentence explanation"
}}
It is mandatory that you respond only using the JSON format above, nothing else.
Your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parsable by a JSON parser without errors."""

            result = (
                gl.nondet.exec_prompt(prompt)
                .replace("```json", "")
                .replace("```", "")
            )
            return json.loads(result)

        result_json = gl.eq_principle.strict_eq(get_verdict)

        verdict = str(result_json.get("verdict", "REVIEW")).upper()
        reasoning = str(result_json.get("reasoning", "Moderated by AI."))
        severity = str(result_json.get("severity_score", 0))

        if verdict not in ("APPROVED", "REJECTED", "REVIEW"):
            verdict = "REVIEW"

        self.verdicts[content_id] = verdict
        self.reasonings[content_id] = reasoning
        self.severity_scores[content_id] = severity
        self.statuses[content_id] = "moderated"
        self.total_moderated = u256(int(self.total_moderated) + 1)

        return result_json

    @gl.public.view
    def get_content(self, content_id: u256) -> dict[str, typing.Any]:
        return {
            "id": int(content_id),
            "content": self.contents[content_id],
            "category": self.categories[content_id],
            "submitter": self.submitters[content_id],
            "status": self.statuses[content_id],
            "verdict": self.verdicts[content_id],
            "severity_score": self.severity_scores[content_id],
            "reasoning": self.reasonings[content_id],
        }

    @gl.public.view
    def get_stats(self) -> dict[str, typing.Any]:
        return {
            "total_submitted": int(self.next_id) - 1,
            "total_moderated": int(self.total_moderated),
        }
