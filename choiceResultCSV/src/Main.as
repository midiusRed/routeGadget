package {
	import flash.display.StageAlign;
	import flash.display.StageScaleMode;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.filesystem.File;
	import flash.filesystem.FileMode;
	import flash.filesystem.FileStream;
	import flash.net.FileFilter;

	import ui.vbase.VBox;
	import ui.vbase.VButton;
	import ui.vbase.VComponent;
	import ui.vbase.VInputText;
	import ui.vbase.VText;
	import ui.vtool.VToolPanel;

	[SWF(width="640",height="480")]
	public class Main extends VComponent {
		private const
			csvInput:VInputText = VToolPanel.createInputText(),
			htmInput:VInputText = VToolPanel.createInputText(),
			outInput:VInputText = VToolPanel.createInputText(),
			infoText:VText = new VText(VText.SELECTION | VText.CENTER)
			;
		private var lastOpenPath:String;

		public function Main() {
			stage.scaleMode = StageScaleMode.NO_SCALE;
			stage.align = StageAlign.TOP_LEFT;
			stage.tabChildren = stage.stageFocusRect = false;

			setSize(stage.stageWidth, stage.stageHeight);
			csvInput.layoutW = htmInput.layoutW = outInput.layoutW = 400;

			infoText.setBaseFormat(16, 0x000066);

			var csvBt:VButton = VToolPanel.createTextButton('Выбрать...', 120);
			csvBt.addClickListener(onCSVSelect);
			var htmBt:VButton = VToolPanel.createTextButton('Выбрать...', 120);
			htmBt.addClickListener(onHtmSelect);
			var outBt:VButton = VToolPanel.createTextButton('Выбрать...', 120);
			outBt.addClickListener(onResultSelect);
			var runBt:VButton = VToolPanel.createTextButton('Сформировать', 160);
			runBt.addClickListener(onRun);
			infoText.maxW = 500;
			infoText.maxH = 160;

			add(new VBox(new <VComponent>[
				new VText(0, '1. Экспорт из WinOrient в RouteGadget формате (*.csv)'),
				new VBox(new <VComponent>[csvInput, csvBt], 8),
				new VText(0, '2. Экспорт из WinOrient в html формате (*.htm)'),
				new VBox(new <VComponent>[htmInput, htmBt], 8),
				new VText(0, '3. Результирующий файл для RouteGadget (resultRG.csv)'),
				new VBox(new <VComponent>[outInput, outBt], 8),
				runBt,
				infoText
			], 10, VBox.VERTICAL | VBox.CENTER), { hCenter:0, vCenter:0 });

			VToolPanel.assign(stage);
			stage.addEventListener(Event.RESIZE, onResize);

			/*
			csvInput.value = '/Volumes/MacHD/orient/rg/result.csv';
			htmInput.value = '/Volumes/MacHD/orient/rg/777.htm';
			outInput.value = '/Volumes/MacHD/orient/rg/out.csv';
			*/
			/*
			csvInput.value = 'Z:\\home\\test1.ru\\www\\testEvent\\result.csv';
			htmInput.value = 'Z:\\home\\test1.ru\\www\\testEvent\\111.htm';
			outInput.value = 'Z:\\home\\test1.ru\\www\\testEvent\\resultRG.csv';
			*/
		}

		private function onResize(event:Event):void {
			geometryPhase();
		}

		private function setInput(file:File, input:VInputText, ex:String = ''):void {
			lastOpenPath = file.parent ? file.parent.nativePath : null;
			input.value = file.nativePath + ex;
		}

		private function onCSVSelect(event:MouseEvent):void {
			var file:File = new File(lastOpenPath);
			file.addEventListener(Event.SELECT, function(event:Event):void { setInput(event.target as File, csvInput); });
			file.browseForOpen('Экспорт из WinOrient в RouteGadget формате', [new FileFilter("csv", "*.csv")]);
		}

		private function onHtmSelect(event:MouseEvent):void {
			var file:File = new File(lastOpenPath);
			file.addEventListener(Event.SELECT, function(event:Event):void { setInput(event.target as File, htmInput); });
			file.browseForOpen('Экспорт из WinOrient в html формате', [new FileFilter("htm", "*.htm;*html")]);
		}

		private function onResultSelect(event:MouseEvent):void {
			var file:File = new File(lastOpenPath);
			file.addEventListener(Event.SELECT, function(event:Event):void { setInput(event.target as File, outInput, File.separator + 'resultRG.csv'); });
			file.browseForDirectory('Папка куда будет помещен результирующй файл');
		}

		private function readFile(file:File):String {
			var fs:FileStream = new FileStream();
			fs.open(file, FileMode.READ);
			var str:String = fs.readMultiByte(fs.bytesAvailable, 'windows-1251');
			fs.close();
			return str;
		}

		private function onRun(event:MouseEvent):void {
			infoText.value = null;
			var csvFile:File = new File(csvInput.value);
			if (!csvFile.exists || csvFile.isDirectory) {
				infoText.value = 'Не удаетмя найти файл для пункта 1';
				return;
			}
			var htmFile:File = new File(htmInput.value);
			if (!htmFile.exists || htmFile.isDirectory) {
				infoText.value = 'Не удаетмя найти файл для пункта 2';
				return;
			}
			var outPath:String = outInput.value;
			if (!outPath) {
				infoText.value = 'Должен быть задан путь для пункта 3';
				return;
			}
			try {
				run(csvFile, htmFile, outPath);
			} catch (error:Error) {
				infoText.value = 'Что-то пошло не так, свяжитесь с разработчиком';
			}
		}

		private function getUInt(str:String):int {
			var v:Number = parseInt(str);
			return isNaN(v) || v < 0 ? 0 : v;
		}

		private function run(csvFile:File, htmFile:File, outPath:String):void {
			var csvList:Array = readFile(csvFile).split('\n');
			var csvCount:uint = csvList.length;
			var htmList:Array = readFile(htmFile).split('\n');
			var htmCount:uint = htmList.length;

			var totalTimePattern:RegExp = new RegExp('<td>(\\d+):(\\d+):(\\d+)');
			var controlList:Vector.<uint> = new Vector.<uint>();
			for (var i:uint = 0; i < csvCount; i++) { //проходим по всем строкам результатов
				if (String(csvList[i]).length == 0) { //пропускаем пустые строки
					continue;
				}
				var athleteList:Array = String(csvList[i]).split(';');
				if (athleteList.length <= 2) { //>2 - признак что в строке результат спортсмена
					continue;
				}
				var nameStr:String = athleteList[0] + ' ' + athleteList[1]; //имя спортсмена которое будет искаться в htm
				for (var j:uint = 0; j < htmCount; j++) { //обходим все строки htm
					if (String(htmList[j]).indexOf(nameStr) >= 0) { //и ищем совпадение с именем
						//нужно получить общее время, чтобы расчитать время финиша
						var totalTimeList:Array = String(htmList[j]).match(totalTimePattern);
						var totalTime:int = 0; //sec
						if (totalTimeList && totalTimeList.length == 4) {
							totalTime = 3600 * int(totalTimeList[1]) + 60 * int(totalTimeList[2]) + int(totalTimeList[3]);
						}
						var splitStr:String = htmList[j + 1]; //сплиты будут находится на строке НИЖЕ
						var k:int = splitStr.indexOf('<tr>'); //может потребоваться отсечь не нужные данные
						if (k >= 0) {
							splitStr = splitStr.substr(0, k);
						}
						controlList.length = 0; //будем вести список кп, для исключение дублирующих
						var bonusMinutes:int = 0; //накопительное время, если будет встречно дублирующее КП
						var bonusSeconds:int = 0;
						var curTotalTime:int = 0;
						var splitList:Array = splitStr.split(')'); //разделяем сплиты
						k = 0;
						while (k < splitList.length) { //итерируемся по сплитам
							splitStr = splitList[k];
							var m:int = splitStr.indexOf('('); //нам нужно получить номер кп и время сплита
							if (m > 0) {
								var control:uint = getUInt(trim(splitStr.substr(m + 1)));
								var timeList:Array = trim(splitStr.substr(0, m), false).split(':');
								if (timeList.length == 3) {
									var minutes:int = getUInt(timeList[0]) * 60 + getUInt(timeList[1]);
									var seconds:int = getUInt(timeList[2]);
									curTotalTime += minutes * 60 + seconds;
									if (controlList.indexOf(control) < 0) {
										controlList.push(control);
										splitList[k] = (minutes + bonusMinutes) + ':' + (seconds + bonusSeconds);
										bonusMinutes = bonusSeconds = 0;
										k++;
										continue;
									} else { //если дублирующий КП
										bonusMinutes += minutes;
										bonusSeconds += seconds;
									}
								}
							}
							splitList.splice(k, 1);
						}
						athleteList.length = 4;
						m = splitList.length;
						for (k = 0; k < m; k++) {
							athleteList.push(splitList[k]);
						}
						if (totalTime > curTotalTime) { //время до финиша
							m = totalTime - curTotalTime;
							athleteList.push(int(m / 60) + ':' + int(m % 60));
						}
						csvList[i] = athleteList.join(',');
						break;
					}
				}
			}

			try {
				var fs:FileStream = new FileStream();
				fs.open(new File(outPath), FileMode.WRITE);
				fs.writeMultiByte(csvList.join('\n'), 'windows-1251');
				fs.close();
			} catch (error:Error) {
				infoText.value = 'Не удалось сохранить результат импорта в ' + outPath;
				return;
			}

			infoText.value = 'ОК. Результат успешно сохранен';
		}

		public static function trim(value:String, isNull:Boolean = false):String {
			if (value.length > 0) {
				//обрезаем пробелы по краям
				var s:int = 0;
				while (value.charCodeAt(s) == 32) {
					s++;
				}
				var e:int = value.length - 1;
				while (value.charCodeAt(e) == 32) {
					e--;
				}
				if (e >= s) {
					return value.substring(s, e + 1);
				}
			}
			return isNull ? null : '';
		}

	} //end class
}