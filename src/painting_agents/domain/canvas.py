from pydantic import BaseModel, Field

from .shapes import Shape


class Canvas(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    shapes: list[Shape] = Field(default_factory=list)

    def add_shape(self, shape: Shape) -> None:
        if any(existing.id == shape.id for existing in self.shapes):
            raise ValueError(f"Shape already exists: {shape.id}")

        self.shapes.append(shape)

    def remove_shape(self, shape_id: str) -> None:
        for index, shape in enumerate(self.shapes):
            if shape.id == shape_id:
                del self.shapes[index]
                return

        raise ValueError(f"Shape not found: {shape_id}")