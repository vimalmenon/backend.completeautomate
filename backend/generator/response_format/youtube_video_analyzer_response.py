from pydantic import BaseModel, Field


class YouTubeVideoAnalyzerResponse(BaseModel):

    title: str = Field(
        description="A concise, engaging, and SEO-friendly video title that reflects the core topic"
    )
    description: str = Field(
        description="A clear video description summarizing the main points, audience value, and context"
    )
    tags: list[str] = Field(
        description="Relevant searchable keywords and phrases for discoverability, based on the video's topic"
    )


class YouTubeVideoAnalyzerListResponse(BaseModel):
    details: list[YouTubeVideoAnalyzerResponse] = Field(
        description="A list of analyzed video outputs, each containing an improved title, description, and tags"
    )
