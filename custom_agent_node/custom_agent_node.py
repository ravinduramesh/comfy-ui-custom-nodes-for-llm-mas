class CustomAgentNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "agent_name": ("STRING", {"default": "MyCustomAgent"}),
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "agents_in": ("LIST", {"subtype": "DICT"}),  # list of agent dicts
            }
        }


    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("agents_out",)
    FUNCTION = "create_agent_list"
    CATEGORY = "Custom/LLM-MAS"


    def create_agent_list(self, agent_name, system_prompt, agents_in=None):
        if agents_in is None:
            agents_in = []

        # Validate structure
        if not isinstance(agents_in, list):
            agents_in = []

        # Add current agent
        new_agent = {
            "name": agent_name,
            "prompt": system_prompt
        }
        agents_in.append(new_agent)

        return (agents_in,)

