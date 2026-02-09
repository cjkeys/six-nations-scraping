import fs from "fs"
import path from "path"

export default function Page() {
  const htmlPath = path.join(process.cwd(), "index.html")
  const htmlContent = fs.readFileSync(htmlPath, "utf-8")

  // Extract the content between <body> and </body>
  const bodyMatch = htmlContent.match(/<body[^>]*>([\s\S]*?)<\/body>/)
  const styleMatch = htmlContent.match(/<style[^>]*>([\s\S]*?)<\/style>/)

  const bodyContent = bodyMatch ? bodyMatch[1] : ""
  const styleContent = styleMatch ? styleMatch[1] : ""

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: styleContent }} />
      <div dangerouslySetInnerHTML={{ __html: bodyContent }} />
    </>
  )
}
