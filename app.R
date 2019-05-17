#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(shinymaterial)
library(DT)
library(reticulate)
options(shiny.maxRequestSize=50*1024^2) 
# Define UI for application that draws a histogram
ui <-  material_page(
  title='志诺维思病历数据归一化系统',
  material_row(
    material_column(width=2,
                    material_card(
                      title='上传JSON文件（utf-8，最大50M）',
                      material_file_input('rawJson','浏览')),
                    material_card(
                      title='下载计算结果',
                      downloadButton("results", "开始下载")),
                    material_card(
                      title='上传归一化配置文件（utf-8）',					  
                      material_file_input('normGuide','浏览')),
                    material_card(
                      title='下载归一化后JSON',
                      downloadButton("normJSON", "开始下载")),
                    material_card(
                      title='导入文件',
                      textOutput("input_files"))
    ),
    material_column(width=3,
                    material_card(
                      title='归一前取值分布',
                      DTOutput('distribution'))),
    material_column(width=3,
                    material_card(
                      title='归一后取值分布',
                      DTOutput('normdistribution'))),
    material_column(width=2,
                    material_card(
                      title='归一前完整性计算',
                      DTOutput('completeness'))),
    material_column(width=2,
                    material_card(
                      title='归一后完整性计算',
                      DTOutput('normcompleteness')))				
  )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
  
  result=reactive({
    #use_python("/usr/local/bin/python3", required=T)
    source_python('data_completeness.py')
    tmp=End(input$rawJson$datapath)
    tmp$freq=unlist(tmp$freq)
    tmp
  })
  
  output$distribution=renderDT(rownames = FALSE,options = list(pageLength = 20,dom='tip'),filter = 'top',{
    withProgress(message = '正在计算', detail = '稍等...',{
      subset(result(),target!='completeness')
    })
  })
  output$completeness=renderDT(rownames = FALSE,options = list(pageLength = 20,dom='tip'),filter = 'top',{
    subset(result(),target=='completeness')
  })
  
  output$results<- downloadHandler(
    filename = function() {
      paste(input$rawJson$name,'_', Sys.Date(),".csv", sep = "")
    },
    content = function(file) {
      write.csv(result(), file, row.names = FALSE,fileEncoding="UTF-8")
    }
  )
  
  normed=reactive({   
    #use_python("/usr/local/bin/python3", required=T)
    source_python('Normalize.py')
    Json_Normalize(input$rawJson$datapath,input$normGuide$datapath)
  })
  norm_result=reactive({
    withProgress(message = '正在计算归一后数据', detail = '稍等...',{
      writeLines(normed(), 'tmp_norm.json')
      #use_python("/usr/local/bin/python3", required=T)
      source_python('data_completeness.py')
      tmp=End('tmp_norm.json')
      tmp$freq=unlist(tmp$freq)
      tmp
    })
  })
  
  output$normdistribution=renderDT(rownames = FALSE,options = list(pageLength = 20,dom='tip'),filter = 'top',{  
    subset(norm_result(),target!='completeness')
  })
  output$normJSON<- downloadHandler(
    filename = function() {
      paste(input$rawJson$name,'_norm_', Sys.Date(),".json", sep = "")
    },
    content = function(file) {
      writeLines(normed(), file)
    }
  )
  output$normcompleteness=renderDT(rownames = FALSE,options = list(pageLength = 20,dom='tip'),filter = 'top',{
    subset(norm_result(),target=='completeness')
  })
  
  output$input_files=renderText({
    paste(input$rawJson$name,input$normGuide$name,sep='和')
    
  })
  
  
}

# Run the application 
shinyApp(ui = ui, server = server)


