package ui.vtool {
	import flash.display.DisplayObject;
	import flash.display.Graphics;
	import flash.display.Sprite;
	import flash.display.Stage;
	import flash.events.Event;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.text.Font;
	import flash.utils.getQualifiedClassName;

	import ui.vbase.SkinManager;
	import ui.vbase.VButton;
	import ui.vbase.VCheckbox;
	import ui.vbase.VComponent;
	import ui.vbase.VEvent;
	import ui.vbase.VFill;
	import ui.vbase.VInputText;
	import ui.vbase.VLabel;
	import ui.vbase.VScrollBar;
	import ui.vbase.VSkin;

	public class VToolPanel extends VComponent {
		public static var instance:VToolPanel;
		private static var keyCode:uint;

		public static function assign(stage:Stage, keyCode:uint = 86):void {
			Font.registerFont(MyriadProFont);
			VToolPanel.keyCode = keyCode;
			stage.addEventListener(KeyboardEvent.KEY_DOWN, onKeyDown);
		}

		public static function clear(stage:Stage):void {
			dispose();
			stage.removeEventListener(KeyboardEvent.KEY_DOWN, onKeyDown);
		}

		private static function onKeyDown(event:KeyboardEvent):void {
			if (event.target.parent is VInputText) {
				return;
			}

			if (event.keyCode == keyCode) {
				if (instance) {
					dispose();
				} else {
					init(event.currentTarget as Stage);
				}
			} else if (instance) {
				if (event.ctrlKey && event.altKey) {
					switch (event.keyCode) {
						case 37: //left
							var obj:Object = { left:10, vCenter:0 };
							break;

						case 39: //right
							obj = { right:10, vCenter:0 };
							break;

						case 38: //top
							obj = { top:10, hCenter:0 };
							break;

						case 40: //bottom:
							obj = { bottom:10, hCenter:0 };
							break;
					}
					if (obj) {
						obj.w = instance.layoutW;
						obj.h = instance.layoutH;
						instance.resetLayout();
						instance.assignLayout(obj);
						instance.syncLayout();
					}
				}
			}
		}

		private static function init(stage:Stage):void {
			if (instance) {
				return;
			}
			ComponentPanel.target = null;
			stage.addEventListener(Event.RESIZE, onStageResize);
			instance = new VToolPanel();
			var canvas:VComponent = new VComponent();
			canvas.add(instance, { right:10, vCenter:0 });
			stage.addChild(instance.drawSprite);
			stage.addChild(instance.layoutPanel).visible = false;
			stage.addChild(canvas);

			onStageResize();
			instance.capturePanel.onTarget();
		}

		private static function dispose():void {
			if (!instance) {
				return;
			}
			var canvas:VComponent = instance.parent as VComponent;
			canvas.stage.removeEventListener(Event.RESIZE, onStageResize);
			canvas.dispose();
			canvas.stage.removeChild(instance.drawSprite);
			instance.layoutPanel.dispose();
			canvas.stage.removeChild(instance.layoutPanel);
			canvas.stage.removeChild(canvas);
			instance = null;
		}

		public static function getClassName(value:*):String {
			var className:String = getQualifiedClassName(value);
			var index:int = className.lastIndexOf('::');
			return className.substr((index == -1) ? 0 : index + 2, className.length);
		}

		public static function drawCounter(target:DisplayObject = null, isGreen:Boolean = false):void {
			var g:Graphics = VToolPanel.instance.drawSprite.graphics;
			g.clear();

			var component:VComponent = target ? target as VComponent : ComponentPanel.target;
			if (component) {
				if (isGreen) {
					g.lineStyle(1, 0x009900);
				} else {
					g.lineStyle(2, 0xFF0000);
				}
				var p:Point = component.localToGlobal(new Point());
				g.drawRect(p.x, p.y, component.w, component.h);
			}
		}

		public static function clearCounter():void {
			instance.drawSprite.graphics.clear();
		}

		/**
		 * Обработчик изменения размеров stage
		 *
		 * @param    event        Объект события Event.RESIZE
		 */
		private static function onStageResize(event:Event = null):void {
			var canvas:VComponent = instance.parent as VComponent;
			canvas.setGeometrySize(canvas.stage.stageWidth, canvas.stage.stageHeight, true);
		}

		public static function createTextButton(text:String, w:int, clickHandler:Function = null, data:* = null, skinName:String = null, variance:uint = 0):VButton {
			var bt:VButton = new VButton();
			bt.setSkin(SkinManager.getEmbed('VToolBt' + (skinName ? skinName : 'Green'), VSkin.STRETCH));
			var label:VLabel = new VLabel(VLabel.CENTER | VLabel.CONTAIN, '<div fontFamily="Myriad Pro" fontSize="16" color="0x000055">' + text + '</div>');
			bt.icon = label;
			bt.add(label, { left:6, right:6, vCenter:0 });
			bt.variance = variance;
			if (clickHandler != null) {
				bt.addListener(MouseEvent.CLICK, clickHandler);
				bt.data = data;
			}
			bt.setSize(w, 28);
			return bt;
		}

		/**
		 * Создает кнопку, размер которой определеяется скином
		 *
		 * @param    skinName            Имя скина
		 * @param    skinMode
		 * @param    icon
		 * @param    iconLayout          Layout-иконки
		 * @return
		 */
		public static function createEmbedButton(skinName:String, skinMode:uint = 0, icon:VComponent = null, iconLayout:Object = null):VButton {
			var skin:VSkin = SkinManager.getEmbed(skinName, skinMode);
			var bt:VButton = new VButton();
			bt.setSize(skin.measuredWidth, skin.measuredHeight);
			bt.setSkin(skin);
			skin.stretch();
			if (icon) {
				bt.icon = icon;
				bt.add(icon, iconLayout);
			}
			return bt;
		}

		public static function createScrollBar():VScrollBar {
			var track:VSkin = SkinManager.getEmbed('VToolTrack', VSkin.STRETCH);
			var thumb:VButton = createEmbedButton('VToolThumb', VSkin.STRETCH);
			var downBt:VButton = createEmbedButton('VToolScrollButton', VSkin.FLIP_Y);
			var upBt:VButton = createEmbedButton('VToolScrollButton');
			var sb:VScrollBar = new VScrollBar(track, thumb, VScrollBar.WHEEL);
			sb.assignButton(upBt, downBt);
			sb.minH = 60;
			sb.add(track, { hCenter:0, top:12, bottom:12 });
			sb.addChild(upBt);
			sb.add(downBt, { bottom:0 });
			sb.add(thumb, { hCenter:0, minH:14, top:12, bottom:12 });
			return sb;
		}

		public static function createCheckbox(text:*, selected:Boolean = false, changeHandler:Function = null):VCheckbox {
			var boxSkin:VSkin = SkinManager.getEmbed('VToolEmptyCkeckbox');
			boxSkin.assignLayout({ w:14, h:14, vCenter:0 });
			var checkSkin:VSkin = SkinManager.getEmbed('VToolCheckLabel');
			checkSkin.assignLayout({ left:2, vCenter:-2 });
			if (text) {
				var label:VComponent = text is VComponent ? text : new VLabel(VLabel.MIDDLE, String(text));
				label.assignLayout({ left:16, hP:100 });
			}
			var cb:VCheckbox = new VCheckbox(boxSkin, checkSkin, label, selected);
			if (changeHandler != null) {
				cb.addListener(VEvent.CHANGE, changeHandler);
			}
			return cb;
		}

		public static function createInputText(fontSize:uint = 12, color:uint = 0xFF0000, mode:uint = 0, paddingH:uint = 6, paddingV:uint = 3):VInputText {
			return new VInputText(mode, SkinManager.getEmbed('VToolBgInputText', VSkin.STRETCH), paddingH, paddingV).setBaseFormat(fontSize, color, 'Myriad Pro') as VInputText;
		}

		public static function createBg():VFill {
			var fill:VFill = new VFill(0xFCFDEE, 1, 15);
			fill.setLine(1, 0x353A55, 0.57);
			return fill;
		}

		public const
			captureBt:VButton = createTextButton('Захват', 90, onChangeTab, null, 'Blue'),
			componentBt:VButton = createTextButton('Компонент', 90, onChangeTab, null, 'Blue'),
			capturePanel:CapturePanel = new CapturePanel(),
			componentPanel:ComponentPanel = new ComponentPanel(),
			drawSprite:Sprite = new Sprite(),
			layoutPanel:LayoutPanel = new LayoutPanel()
			;

		public function VToolPanel() {
			setSize(200, 220);

			addStretch(createBg());

			add(captureBt, { left:5, top:5 });
			add(componentBt, { left:100, top:5 });
			onChangeTab(captureBt);
		}

		/**
		 * Обработчик смены вкладки
		 *
		 * @param    data        Объект события MouseEvent.CLICK || VButton
		 */
		public function onChangeTab(data:Object):void {
			var bt:VButton = ((data is MouseEvent) ? (data as MouseEvent).currentTarget : data) as VButton;
			bt.disabled = true;

			if (bt == captureBt) {
				if (componentPanel.parent) {
					remove(componentPanel, false);
				}
				componentBt.disabled = false;
				var panel:VComponent = capturePanel;
			} else {
				if (capturePanel.parent) {
					remove(capturePanel, false);
				}
				captureBt.disabled = false;
				panel = componentPanel;
			}
			add(panel, { left:5, right:5, top:37, bottom:5 });

			if (ComponentPanel.target) {
				if (panel == componentPanel) {
					clearCounter();
					componentPanel.update(null, true);
				} else {
					layoutPanel.assign(null);
					drawCounter();
				}
			}
		}

	} //end class
}