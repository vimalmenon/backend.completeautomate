from backend.services.task.pending_task import PendingTask
from backend.services.task.start_new_task import StartNewTask
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
        # NewIdeaTask().input(
        #     task="""
        #         ### **3) Header Component**
        #         - **Instructions**:
        #         - Create responsive header with logo on left and navigation on right
        #         - Implement mobile hamburger menu with smooth slide-in animation
        #         - Add sticky header functionality that appears on scroll
        #         - Include navigation items: Home, Services, About, Contact
        #         - Ensure accessibility with proper ARIA labels and keyboard navigation
        #     """
        # )

        # NewIdeaTask().input(
        #     task="""
        #     Our team is building a website for our company.
        #     Breakdown the tasks for building the complete website.
        #     Only include frontend tasks for frontend developers.
        #     Breakdown the tasks to very small chunks with detailed instructions.
        #     It should include all the pages required for a complete website.
        #     """
        # )
        NewIdeaTask().input(
            task="""
            I want to create a image for youtube banner, 
            it should show properly for mobile and desktop both.
            Make it visually appealing and relevant to my channel's content.
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
