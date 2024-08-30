from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Token,
)

__all__ = ["AyuMirage"]


class AyuMirage(Style):
    name = "ayu_mirage"

    background_color = "#1f2430"
    highlight_color = "#1a1f29"

    line_number_background_color = "#1f2430"
    line_number_color = "#8a919966"

    styles = {
        Comment: "#64768B",
        Error: "#FF6666",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.Deleted: "#FF6666",
        Generic.Error: "#FF6666",
        Generic.Inserted: "#87D96C",
        Keyword: "#FFAD66",
        Keyword.Operator: "#FFAD66",
        Literal: "#af875f",
        Name: "#73D0FF",
        Name.Function: "#FFD173",
        Name.Tag: "#5CCFE6",
        Name.Import: "#D5FF80",
        Name.Package: "#D5FF80",
        Number: "#DFBFFF",
        Operator: "#F29E74",
        Punctuation: "#CCCAC2",
        String: "#D5FF80",
        String.Regex: "#95E6CB",
        String.Other.Link: "#5CCFE6",
        Token: "#6796E6",
    }
