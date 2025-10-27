set distpath=%CD%\dist
cd YTMediaTool
pyinstaller -y --distpath "%distpath%" YTMediaTool.spec
cd ..
copy "LICENSE" "dist\YTMediaTool\LICENSE.txt"
xcopy /s/v "include" "dist\YTMediaTool"
explorer dist
