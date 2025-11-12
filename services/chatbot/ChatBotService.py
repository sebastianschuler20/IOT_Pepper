from abc import ABC, abstractmethod

class ChatbotService(ABC):
    """
    Abstract base class (Interface) for a Chatbot Service.
    """

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generates a response for the given prompt.
        Must be implemented by subclasses.

        Args:
            prompt (str): The input prompt for the chatbot.

        Returns:
            str: The chatbot's generated response.
        """
        pass
