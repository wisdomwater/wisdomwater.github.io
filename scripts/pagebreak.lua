function Div(el)
    if el.classes:includes("pagebreak") then
        if FORMAT:match("epub") or FORMAT:match("html") then
            return pandoc.RawBlock("html", '<div class="pagebreak"></div>')
        elseif FORMAT:match("latex") then
            return pandoc.RawBlock("latex", "\\newpage")
        elseif FORMAT:match("docx") then
            -- Insert a WordML page break for .docx output
            return pandoc.RawBlock("openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        else
            return nil
        end
    end
    return nil
end
