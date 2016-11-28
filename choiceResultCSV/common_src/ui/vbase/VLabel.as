package ui.vbase {
	import flash.display.Sprite;
	import flash.geom.Rectangle;

	import flashx.textLayout.compose.IFlowComposer;
	import flashx.textLayout.container.ContainerController;
	import flashx.textLayout.container.ScrollPolicy;
	import flashx.textLayout.conversion.ConversionType;
	import flashx.textLayout.conversion.TextConverter;
	import flashx.textLayout.conversion.TextLayoutImporter;
	import flashx.textLayout.edit.SelectionManager;
	import flashx.textLayout.elements.LinkElement;
	import flashx.textLayout.elements.TextFlow;
	import flashx.textLayout.events.FlowElementMouseEvent;
	import flashx.textLayout.formats.LeadingModel;
	import flashx.textLayout.formats.LineBreak;
	import flashx.textLayout.formats.TextAlign;
	import flashx.textLayout.formats.VerticalAlign;
	import flashx.textLayout.tlf_internal;

	public class VLabel extends VComponent {
		public static const
			MIDDLE:uint = 1, //размещение по вертикальному центру
			CONTAIN:uint = 2, //режим вписывания
			CENTER:uint = 4,
			CONTAIN_CENTER:uint = CONTAIN | CENTER,
			LEADING_BOX:uint = 8,
			IMG_HINT:uint = 16 | LEADING_BOX, //может использоваться подсказка на картинках
			SELECTION:uint = 32
			;
		protected static const importer:TextLayoutImporter = new TextLayoutImporter();
		
		protected var
			textFlow:TextFlow,
			//попытки использования в качестве контайнера под текст самого компонента приводят к тому, что при очистке
			//ширина и высота остаются равными старому размеру (должны 0,0),
			//и при следующем добавлении текста он начинает вести себя местами неадекватно
			content:Sprite,
			contentBuildSize:uint = uint.MAX_VALUE //см описание VText.contentBuildSize
			;
		
		public function VLabel(mode:uint = 0, text:String = null) {
			mouseEnabled = false;
			this.mode = mode;
			this.text = text;
		}
		
		public function set text(value:String):void {
			if (textFlow) {
				clearText();
				textFlow = null;
			}
			
			if (value != null && value.length > 0) {
				try {
					textFlow = importer.createTextFlowFromXML(
						new XML('<TextFlow xmlns="http://ns.adobe.com/textLayout/2008" version="3.0.0">' + value + '</TextFlow>')
					);
					if ((mode & LEADING_BOX) != 0) {
						textFlow.leadingModel = LeadingModel.BOX;
					}
					if ((mode & CONTAIN) != 0) {
						textFlow.lineBreak = LineBreak.EXPLICIT;
					}
					if ((mode & CENTER) != 0) {
						textFlow.textAlign = TextAlign.CENTER;
					}
					if ((mode & MIDDLE) != 0) {
						textFlow.verticalAlign = VerticalAlign.MIDDLE;
					}
					if ((mode & SELECTION) != 0) {
						mouseChildren = true;
						textFlow.interactionManager = new SelectionManager();
						textFlow.addEventListener('click', onClick, false, 0, true);
					} else {
						mouseChildren = (mode & IMG_HINT) != 0;
					}
				} catch (error:Error) {
					CONFIG::debug {
						trace('Не собрался TextFlow:', value);
					}
				}
			}

			contentBuildSize = uint.MAX_VALUE;
			syncContentSize(true);
		}

		private function onClick(event:FlowElementMouseEvent):void {
			if (event.flowElement is LinkElement) {
				dispatcher.dispatchEvent(new VEvent(VEvent.SELECT, (event.flowElement as LinkElement).href));
			}
		}
		
		public function get text():String {
			return textFlow ? textFlow.getText() : null;
		}

		override public function setMode(value:uint, isSetBit:Boolean = true):void {
			super.setMode(value, isSetBit);
			text = tlfText;
		}
		
		public function get tlfText():String {
			if (textFlow) {
				var str:String = TextConverter.export(textFlow, TextConverter.TEXT_LAYOUT_FORMAT, ConversionType.STRING_TYPE) as String;
				if (str && str.substr(0, 9) == '<TextFlow') { //срежим обрамляющий TextFlow
					var i:int = str.indexOf('>');
					if (i > 0) {
						//</TextFlow> len == 11
						str = str.slice(i + 1, -11);
					}
				}
			}
			return str;
		}
		
		override public function dispose():void {
			clearText();
			super.dispose();
		}
		
		private function clearText():void {
			if (textFlow) {
				textFlow.flowComposer.removeAllControllers();
			}
			if (content) {
				removeChild(content);
				content = null;
			}
		}
		
		protected function buildText(compositionWidth:Number, compositionHeight:Number):void {
			clearText();
			
			content = new Sprite();
			addChild(content);
			var composer:IFlowComposer = textFlow.flowComposer;
			var cc:ContainerController = new ContainerController(content, compositionWidth, compositionHeight);
			cc.verticalScrollPolicy = ScrollPolicy.OFF;
			composer.addController(cc);
			composer.updateAllControllers();
		}

		//смотри описание VText.measuredWidth
		override public function get measuredWidth():uint {
			if (validContentSize && layoutW <= 0) {
				VText.checkValidContentSize(this, contentBuildSize, (mode & CONTAIN) != 0);
			}
			return super.measuredWidth;
		}

		override public function get measuredHeight():uint {
			if (validContentSize && layoutH <= 0) {
				VText.checkValidContentSize(this, contentBuildSize, (mode & CONTAIN) != 0);
			}
			return super.measuredHeight;
		}
		
		override protected function calcContentSize():void {
			if (textFlow) {
				var w:uint = VText.getComposeW(this, (mode & CONTAIN) != 0);
				var h:uint = VText.getComposeH(this);
				contentBuildSize = VText.getContentBuildSize(w, h);
				buildText(w > 0 ? w : NaN, h > 0 ? h : NaN);
				
				const cc:ContainerController = textFlow.flowComposer.getControllerAt(0);
				contentW = Math.ceil(cc.tlf_internal::contentWidth);
				updateW = (w > contentW) ? w : contentW;
				if ((mode & LEADING_BOX) != 0) {
					var rect:Rectangle = content.getRect(null);
					contentH = Math.ceil(rect.height + rect.y);
				} else {
					contentH = Math.ceil(cc.tlf_internal::contentHeight);
				}
				updateH = (h > contentH) ? h : contentH;
			}
		}
		
		override protected function customUpdate():void {
			if (textFlow) {
				buildText(w, h);
				
				//вписывание
				if ((mode & CONTAIN) != 0) {
					var cc:ContainerController = textFlow.flowComposer.getControllerAt(0);
					var textW:uint = Math.ceil(cc.tlf_internal::contentWidth);
					
					if (textW > w) {
						buildText(textW, h);
						
						var y:Number = cc.tlf_internal::contentTop;
						var textH:Number = content.height;
						VSkin.contain(content, w, h, true);
						
						//идет вписывание в ширину и content.x остается на месте
						//строки выравниваются по dominantBaseline, поэтому требуется коррекция y
						content.y = Math.ceil(y * (1 - content.scaleY) + (textH - content.height) / 2);
					}
				}
			}
		}
		
		override public function add(component:VComponent, layout:Object = null, index:int = -1):void {
			throw new Error('VLabel no use add method');
		}
		
		override public function remove(component:VComponent, isDispose:Boolean = true):void {
			throw new Error('VLabel no use remove method');
		}


		CONFIG::debug
		override public function getToolPropList(out:Array):void {
			var str:String = tlfText;
			out.push(
				new VOComponentItem('text', VOComponentItem.TEXT, str ? str.replace('\n', '') : ''),
				new VOComponentItem('contain', VOComponentItem.CHECKBOX, null, (mode & VLabel.CONTAIN) != 0, VLabel.CONTAIN),
				new VOComponentItem('middle', VOComponentItem.CHECKBOX, null, (mode & VLabel.MIDDLE) != 0, VLabel.MIDDLE),
				new VOComponentItem('center', VOComponentItem.CHECKBOX, null, (mode & VLabel.CENTER) != 0, VLabel.CENTER)
			);
		}

		CONFIG::debug
		override public function updateToolProp(item:VOComponentItem):void {
			if (item.key == 'text') {
				text = item.value as String;
			} else {
				setMode(item.bit, item.checkbox);
			}
		}

	} //end class
}