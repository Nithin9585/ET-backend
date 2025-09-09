from __future__ import annotations
import json
import logging
import re
from typing import List, Dict, Any, Tuple
import anyio
import google.generativeai as genai
from .models import DetectedEntity

class LLMValidator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def validate_entities(self, entities: List[DetectedEntity], context_text: str, detector=None) -> Tuple[List[DetectedEntity], List[Dict[str, Any]]]:
        validated_entities = []
        false_positives = []
        for entity in entities:
            context = self._build_context(entity, context_text)
            validation_result = await self._validate_with_llm(entity, context)
            entity.validations["llm_contextual_score"] = validation_result["confidence"]
            entity.validations["llm_reasoning"] = validation_result["reasoning"]
            corrected_type = validation_result.get("corrected_type")
            corrected_value = validation_result.get("corrected_value")
            if corrected_type and corrected_type != entity.type:
                entity.type = corrected_type
                entity.validations["llm_type_correction"] = corrected_type
            if corrected_value and corrected_value != entity.value:
                entity.value = corrected_value
                entity.validations["llm_value_correction"] = corrected_value
                if detector is not None:
                    entity.redacted_value = detector._mask_value(corrected_value, corrected_type or entity.type)
                else:
                    entity.redacted_value = corrected_value
            entity.confidence = (entity.confidence + validation_result["confidence"]) / 2
            entity.method = "hybrid" if entity.method in ["rule", "ner"] else "llm"
            if validation_result["confidence"] < 0.3 or "misclassified" in validation_result["reasoning"].lower() or "false positive" in validation_result["reasoning"].lower():
                false_positives.append({"type": str(entity.type), "reason": validation_result["reasoning"]})
            else:
                validated_entities.append(entity)
        return validated_entities, false_positives

    def _build_context(self, entity: DetectedEntity, full_text: str) -> str:
        return full_text[:200] + "..." if len(full_text) > 200 else full_text

    async def _validate_with_llm(self, entity: DetectedEntity, context: str) -> Dict[str, Any]:
        import anyio
        prompt = (
            "Analyze if the detected entity is correctly identified and, if needed, suggest corrections.\n\n"
            f"Context: {context}\n"
            f"Detected Entity: {entity.value} (type: {entity.type})\n\n"
            "Consider:\n"
            f"1. Is this actually a {entity.type}?\n"
            "2. Does the surrounding context support this identification?\n"
            "3. Could this be a false positive?\n"
            "4. If the entity type or value should be corrected (e.g., 'date' should be 'date of birth'), provide the corrected type and value.\n\n"
            "Respond ONLY with minified JSON object with keys: confidence (0..1), reasoning, corrected_type (optional), corrected_value (optional)."
        )
        try:
            with anyio.move_on_after(20) as cancel_scope:
                response = await anyio.to_thread.run_sync(lambda: self.model.generate_content(prompt))
            if cancel_scope.cancel_called:
                raise TimeoutError("LLM validation timed out.")
            response_text = getattr(response, "text", None) or ""
            clean = response_text.strip()
            clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
            clean = re.sub(r"\s*```$", "", clean)
            try:
                result = json.loads(clean)
            except Exception:
                match = re.search(r"{.*}", clean)
                result = json.loads(match.group(0)) if match else {"confidence": 0.0, "reasoning": "Could not parse LLM response."}
            if "confidence" not in result:
                result["confidence"] = 0.0
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided."
            return result
        except Exception as e:
            return {"confidence": 0.0, "reasoning": str(e)}
