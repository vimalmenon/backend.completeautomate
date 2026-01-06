from backend.services.task.pending_task import PendingTask
from backend.services.task.start_new_task import StartNewTask
from backend.services.task.scrum_master_task import ScrumMasterAgent
from backend.services.task.new_idea_task import NewIdeaTask


class AppService:

    def start(self) -> None:
        # Start new Ideas
        # NewIdeaTask().input(
        #     task="""
        #     Our team is building a website for our company. 
        #     Breakdown the tasks and provide list of work to be done by Front-End Developers.
        #     Ensure task are specific to front-end development and cover all necessary aspects such as UI design, responsiveness, user experience.
        #     Provide detailed instructions for each task to be performed by developers.
        #     Breakdown the tasks in smaller work items that can be easily assigned and tracked.
        #     Provide me the list of tasks in a structured format.
        #     for e.g.
        #     1) Task 1
        #         create header component
        #         - Instructions: Use React to create a header component that includes the company logo, navigation menu
        #         create footer component
        #         - Instructions: Design a footer component that contains contact information, social media links
        #     I want more detailed breakdown than this.
        #     """
        # )
        NewIdeaTask().input(
            task="""
                ### **3) Header Component**
                - **Instructions**:
                - Create responsive header with logo on left and navigation on right
                - Implement mobile hamburger menu with smooth slide-in animation
                - Add sticky header functionality that appears on scroll
                - Include navigation items: Home, Services, About, Case Studies, Contact
                - Add CTA button "Get Free Consultation" with hover effects
                - Ensure accessibility with proper ARIA labels and keyboard navigation
            """
        )
        # Get Human Confirmation
        # HumanInputTask().confirm()
        # Get pending tasks
        # PendingTask().check()
        # Prepare next tasks
        # ScrumMasterAgent().check()
        # Start next tasks
        # StartNewTask().check()

        # print(
        #     CompanyDetailUtility(
        #         "AI Automation Service Provider",
        #         responsibility="driving innovation and excellence in automation solutions",
        #     ).company_values
        # )
