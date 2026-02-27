"""Project data model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class Project:
    """Represents a laser cutting project."""
    
    path: str
    name: str
    origin: str = "Diversos"
    
    # Flags
    favorite: bool = False
    done: bool = False
    good: bool = False
    bad: bool = False
    analyzed: bool = False
    
    # Metadata
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    ai_description: str = ""
    
    # Structure analysis
    structure: Optional[Dict[str, Any]] = None
    
    # Timestamps
    added_date: str = field(default_factory=lambda: datetime.now().isoformat())
    description_generated_at: str = ""
    
    # Model tracking
    analyzed_model: str = ""
    description_model: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "origin": self.origin,
            "favorite": self.favorite,
            "done": self.done,
            "good": self.good,
            "bad": self.bad,
            "analyzed": self.analyzed,
            "categories": self.categories,
            "tags": self.tags,
            "ai_description": self.ai_description,
            "structure": self.structure,
            "added_date": self.added_date,
            "description_generated_at": self.description_generated_at,
            "analyzed_model": self.analyzed_model,
            "description_model": self.description_model,
        }
    
    @classmethod
    def from_dict(cls, path: str, data: Dict[str, Any]) -> "Project":
        """Create Project from dictionary."""
        # Handle legacy 'category' field
        if "category" in data and "categories" not in data:
            old_cat = data.get("category", "")
            data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
        
        return cls(
            path=path,
            name=data.get("name", ""),
            origin=data.get("origin", "Diversos"),
            favorite=data.get("favorite", False),
            done=data.get("done", False),
            good=data.get("good", False),
            bad=data.get("bad", False),
            analyzed=data.get("analyzed", False),
            categories=data.get("categories", []),
            tags=data.get("tags", []),
            ai_description=data.get("ai_description", ""),
            structure=data.get("structure"),
            added_date=data.get("added_date", datetime.now().isoformat()),
            description_generated_at=data.get("description_generated_at", ""),
            analyzed_model=data.get("analyzed_model", ""),
            description_model=data.get("description_model", ""),
        )
