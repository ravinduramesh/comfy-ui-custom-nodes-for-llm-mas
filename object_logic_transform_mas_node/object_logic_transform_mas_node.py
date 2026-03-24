import random
import io
import sys
from openai import OpenAI


# ---------------------------
# CONFIG
# ---------------------------
MODEL = "llama3"
BASE_URL = "http://localhost:11434/v1"


client = OpenAI(
    base_url=BASE_URL,
    api_key="ollama"
)


# ---------------------------
# LLM CALL
# ---------------------------
def run_llm(system_prompt: str, user_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


THREED_PRINT_PROMPT = """
You are the ThreeDPrintSpecialist agent.
You convert the input description into a single, finite, non-recursive, physically coherent, 3D-printable sculpture.
IMPORTANT: Do not remove or add any objects, organisms, or humans.
IMPORTANT: Keep every single detail of the input but convert the entire form into one manufacturable sculpture.
IMPORTANT: Keep all key objects, organisms, and humans in the input description.

Ensure solid geometry, surface continuity, minimum thickness, and manufacturability. Preserve all uncanny aesthetics exactly as they appear in the input.
Your entire output must be ONLY the single transformed description as one paragraph about the sculpt. No explanations. No additional text. No quotes. Just the description of the sculpture.
"""


# ---------------------------
# ORCHESTRATOR
# ---------------------------
class UncannyOrchestrator:
    def __init__(self, max_steps: int):
        self.max_steps = max_steps


    def run(self, description: str, prompts: dict, agent_names: list, log_buffer) -> str:
        steps = 0


        log_buffer.write("\n[ITERATIVE RANDOM LOOP]\n\n")


        while steps < (self.max_steps - 1):
            next_agent_name = random.choice(agent_names)


            description = run_llm(prompts[next_agent_name], description)


            log_buffer.write(f"[AGENT: {next_agent_name}]\n")
            log_buffer.write(description + "\n")
            log_buffer.write("-" * 60 + "\n")


            steps += 1


        log_buffer.write("\n[FINAL OUTPUT FROM 3D PRINT SPECIALIST]\n\n")


        description = run_llm(THREED_PRINT_PROMPT, description)


        log_buffer.write(description + "\n")
        log_buffer.write("=" * 60 + "\n")


        return description


# ---------------------------
# COMFYUI NODE
# ---------------------------
class ObjectLogicTransformMasNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "steps": ("INT", {"default": 9, "min": 1, "max": 20}),
            },
            "optional": {
                "custom_agents": ("LIST", {"subtype": "DICT"}),
            }
        }


    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("transformed_text", "logs")
    FUNCTION = "process"
    CATEGORY = "Custom/LLM-MAS"


    def process(self, text, steps, custom_agents=None):
        log_buffer = io.StringIO()


        try:
            # ---------------------------
            # Build Dynamic MAS
            # ---------------------------
            dynamic_prompts = dict()
            dynamic_agent_names = []
            
            if custom_agents is not None:
            	if isinstance(custom_agents, dict):
            	    custom_agents = [custom_agents]


            	for agent in custom_agents:
                    name = agent.get("name", "")
                    prompt = agent.get("prompt", "")
                    prompt = prompt + "\n IMPORTANT: Do not remove or add any objects, organisms, or humans. \n IMPORTANT: Keep every single key detail of the input text and make your changes on them."
                
                    if prompt.strip() != "":
                        dynamic_prompts[name] = prompt
                        dynamic_agent_names.append(name)


            # ---------------------------
            # Run Orchestrator
            # ---------------------------
            orchestrator = UncannyOrchestrator(max_steps=steps)


            result = orchestrator.run(
                text,
                dynamic_prompts,
                dynamic_agent_names,
                log_buffer
            )


            logs = log_buffer.getvalue()


        except Exception as e:
            logs = f"[ERROR]\n{str(e)}"
            result = text


        return (result, logs)

