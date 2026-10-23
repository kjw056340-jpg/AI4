$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = $PSScriptRoot
$assets = Join-Path $root 'assets'
New-Item -ItemType Directory -Path $assets -Force | Out-Null
$font = [System.Drawing.Font]::new('Malgun Gothic', 23)
$small = [System.Drawing.Font]::new('Malgun Gothic', 18)
$large = [System.Drawing.Font]::new('Malgun Gothic', 32, [System.Drawing.FontStyle]::Bold)
$ink = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#18344D'))
$muted = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#506579'))
$blue = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#E4F0FF'))
$green = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#DCF2E7'))
$amber = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#FFF0D4'))
$pen = [System.Drawing.Pen]::new([System.Drawing.ColorTranslator]::FromHtml('#557B9C'), 4)
$pen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
$fmt = [System.Drawing.StringFormat]::new()
$fmt.Alignment = [System.Drawing.StringAlignment]::Center
$fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
function Start-Graphic([string]$title, [string]$subtitle, [int]$height = 640) {
    $script:bmp = [System.Drawing.Bitmap]::new(1440, $height)
    $script:g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear([System.Drawing.Color]::White)
    $g.DrawString($title, $large, $ink, 50, 30)
    $g.DrawString($subtitle, $small, $muted, 52, 100)
}
function Box([int]$x,[int]$y,[int]$w,[int]$h,[string]$label,$brush = $blue) {
    $g.FillRectangle($brush, $x,$y,$w,$h)
    $g.DrawString($label,$font,$ink,[System.Drawing.RectangleF]::new($x+12,$y+8,$w-24,$h-16),$fmt)
}
function Arrow([int]$x,[int]$y,[int]$endX,[int]$endY) { $g.DrawLine($pen,$x,$y,$endX,$endY) }
function Save-Graphic([string]$name) {
    $bmp.Save((Join-Path $assets $name),[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
}
Start-Graphic 'Python에서 API 검증까지' '자료가 확인된 학습 흐름 · Day5는 별도 원본 미확인'
Box 50 180 290 135 "Day1`n조건과 반복"
Box 400 180 290 135 "Day2`n자료구조와 가공"
Box 750 180 290 135 "Day3`n객체와 예외"
Box 1100 180 290 135 "Day4`n대입과 교환"
Arrow 345 247 392 247; Arrow 695 247 742 247; Arrow 1045 247 1092 247
Box 50 390 290 135 "보충 FastAPI`n요청과 응답" $amber
Box 400 390 290 135 "Day6`n데이터 검증"
Box 750 390 290 135 "Day7`n비동기와 HTTP"
Box 1100 390 290 135 "Day8`n계약과 테스트" $green
Arrow 345 457 392 457; Arrow 695 457 742 457; Arrow 1045 457 1092 457
$g.DrawString('먼저 동작을 만들고, 입력과 실패를 다루고, 기대한 동작을 검증합니다.',$small,$muted,52,575)
Save-Graphic '01-roadmap.png'

Start-Graphic '조건은 프로그램의 길을 나눕니다' 'Day1 · input → 형 변환 → 판단 → 결과'
Box 50 250 250 130 "입력`n문자열"
Box 370 250 250 130 "int() 변환`n숫자"
Box 700 250 300 130 "score >= 60`n조건 판단"
Box 1110 175 270 110 '참 → 합격' $green
Box 1110 410 270 110 '거짓 → 불합격' $amber
Arrow 305 315 360 315; Arrow 625 315 690 315; Arrow 1005 285 1100 230; Arrow 1005 350 1100 465
$g.DrawString('60점은 합격에 포함됩니다. 숫자가 아닌 입력은 별도 예외 처리가 필요합니다.',$small,$muted,52,570)
Save-Graphic '02-flow.png'

Start-Graphic '객체는 상태와 동작을 함께 가집니다' 'Day3 · 같은 클래스로 만든 객체도 각자의 상태를 가집니다'
Box 470 170 500 100 'BaristaBot 클래스'
Box 80 365 570 180 "로봇 A`n원두 50g · 추출 수 0잔`nbrew_espresso(2)" $blue
Box 790 365 570 180 "로봇 B`n원두 100g · 추출 수 0잔`nbrew_espresso(3)" $green
Arrow 590 275 365 350; Arrow 850 275 1075 350
$g.DrawString('A의 원두를 사용해도 B의 원두량은 바뀌지 않습니다.',$small,$muted,52,575)
Save-Graphic '03-object.png'

Start-Graphic '데이터를 믿기 전에 규칙을 확인합니다' 'Day6 · 구조 → 타입 → 범위 → 필드 사이의 관계'
Box 50 230 280 150 "원시 입력`ndict / JSON"
Box 425 230 470 150 "Pydantic 모델`nField · validator"
Box 1030 170 355 130 "통과`n사용 가능한 모델" $green
Box 1030 410 355 130 "실패`n오류 위치와 원인" $amber
Arrow 335 305 415 305; Arrow 900 270 1020 235; Arrow 900 345 1020 475
$g.DrawString('자동 변환과 엄격한 검사는 다른 정책입니다. strict=True 여부를 확인하세요.',$small,$muted,52,580)
Save-Graphic '04-validation.png'

Start-Graphic '기다리는 시간을 겹치면 어떻게 달라질까요?' 'Day7 · 각각 2초 대기하는 두 작업 · 설명용 가정, 실제 측정 아님' 720
foreach($tick in 0..4) {
    $x = 300 + $tick * 250
    $g.DrawLine([System.Drawing.Pens]::LightGray,$x,200,$x,590)
    $g.DrawString("${tick}초",$small,$muted,$x-20,615)
}
$g.DrawString('순차 / 커피',$small,$ink,50,235)
$g.DrawString('순차 / 차',$small,$ink,50,325)
$g.DrawString('동시 / 커피',$small,$ink,50,445)
$g.DrawString('동시 / 차',$small,$ink,50,535)
Box 300 220 500 65 '2초 대기' $blue
Box 800 310 500 65 '2초 대기' $blue
Box 300 430 500 65 '2초 대기' $green
Box 300 520 500 65 '2초 대기' $green
$g.DrawString('순차: 약 4초 / 동시: 약 2초 + 실행 비용',$small,$muted,52,670)
Save-Graphic '05-concurrency.png'

Start-Graphic '실패한 요청은 다음 성공을 망가뜨리면 안 됩니다' 'Day8 · 전체 정원 4석 · 먼저 검사하고 성공할 때만 상태를 바꿉니다'
Box 50 220 390 190 "3석 예약 요청`n201 성공`n남은 좌석 1" $green
Box 525 220 390 190 "2석 예약 요청`n409 거절`n남은 좌석 1 유지" $amber
Box 1000 220 390 190 "1석 예약 요청`n201 성공`n남은 좌석 0" $green
Arrow 445 315 515 315; Arrow 920 315 990 315
$g.DrawString('검증 대상: 상태 코드 + 응답 본문 + 실패 뒤의 데이터 + 다음 요청의 결과',$small,$muted,52,490)
$g.DrawString('HTTPException은 앞에서 변경한 메모리 값을 자동으로 되돌리지 않습니다.',$small,$muted,52,550)
Save-Graphic '06-reservation.png'

foreach($name in @('architecture.png','parameters.png')) {
    Copy-Item -LiteralPath (Join-Path 'C:\Users\Playdata\dev\05.FastAPI-uvicorn\assets' $name) -Destination (Join-Path $assets $name)
}
$md = Join-Path $root '수업내용정리.md'
$body = (ConvertFrom-Markdown -LiteralPath $md).Html
$html = @"
<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>수업내용정리</title><style>
body{font-family:'Malgun Gothic',sans-serif;max-width:1000px;margin:48px auto;padding:0 24px;color:#203247;line-height:1.85;background:#fff}h1{font-size:42px}h2{margin-top:68px;padding-top:18px;border-top:2px solid #dce8f1;font-size:29px}h3{margin-top:30px}img{max-width:100%;height:auto}table{width:100%;border-collapse:collapse;font-size:14px;display:block;overflow:auto}td,th{border:1px solid #dce2e8;padding:10px;text-align:left}th{background:#edf4fb}pre{background:#142b41;color:#eef4fa;padding:20px;overflow:auto;border-radius:6px;font-size:14px;line-height:1.65}code{font-family:Consolas,'Malgun Gothic',monospace}blockquote{border-left:4px solid #3982b9;margin:20px 0;padding:8px 20px;background:#f0f6fb}a{color:#146eaa}nav{line-height:2.1} @media(max-width:600px){body{margin:24px auto;padding:0 16px}h1{font-size:32px}h2{font-size:24px}}
</style></head><body>$body</body></html>
"@
[System.IO.File]::WriteAllText((Join-Path $root '수업내용정리.html'),$html,[System.Text.UTF8Encoding]::new($false))
$importFiles = @($md,$assets)
Compress-Archive -LiteralPath $importFiles -DestinationPath (Join-Path $root '수업내용정리_Notion가져오기.zip') -Force
Get-ChildItem $root -File | Select-Object Name,Length
Get-ChildItem $assets -File | Select-Object Name,Length
