package ui.vbase {
	import flash.display.MovieClip;
	import flash.events.EventDispatcher;
	import flash.events.MouseEvent;
	import flash.geom.ColorTransform;

	public class VButton extends VComponent {
		public static const //состояния
			UP:uint = 0,
			OVER:uint = 1,
			DOWN:uint = 2,
			DISABLED:uint = 3
			;
		private var
			downFlag:Boolean,
			state:uint = UP
			;
		public var
			skin:VComponent,
			icon:VComponent,
			changeStateFunc:Function = defaultButtonChangeState,
			variance:uint,
			data:Object
			;

		public function VButton() {
			mouseChildren = false;
			buttonMode = true;
			
			addListener(MouseEvent.ROLL_OVER, onMouse);
			addListener(MouseEvent.ROLL_OUT, onMouse);
			addListener(MouseEvent.MOUSE_DOWN, onMouse);
			addListener(MouseEvent.MOUSE_UP, onMouse);
		}
		
		/**
		 * Задать фон
		 * 
		 * @param	value		VComponent
		 */
		public function setSkin(value:VComponent):void {
			if (skin) {
				remove(skin);
			}
			skin = value;
			if (value) {
				CONFIG::debug {
					if (value is VSkin) {
						value.setMode(V_TOOL_HIDDEN);
					}
				}
				addStretch(value, 0);
			}
		}
		
		/**
		 * Задать иконку
		 * 
		 * @param	value		VComponent
		 * @param	layout		Параметры компоновки
		 */
		public function setIcon(value:VComponent, layout:Object = null):void {
			if (icon) {
				remove(icon);
			}
			icon = value;
			if (value) {
				add(value, layout);
			}
		}
		
		public function set disabled(value:Boolean):void {
			if ((state == DISABLED) != value) {
				changeState(value ? DISABLED : UP);
				mouseEnabled = !value;
			}
		}
		
		public function get disabled():Boolean {
			return state == DISABLED;
		}
		
		private function onMouse(event:MouseEvent):void {
			if (state == DISABLED) {
				return;
			}
			switch (event.type) {
				case MouseEvent.ROLL_OVER:
					if (downFlag && !event.buttonDown) {
						downFlag = false;
					}
					var newState:uint = downFlag ? DOWN : OVER;
					break;
					
				case MouseEvent.MOUSE_DOWN:
					downFlag = true;
					newState = DOWN;
					break;
					
				case MouseEvent.MOUSE_UP:
					newState = OVER;
					break;
					
				default:
					newState = UP;
			} //end switch
			changeState(newState);
		}
		
		private function changeState(newState:uint):void {
			if (newState != state) {
				if (changeStateFunc != null) {
					changeStateFunc(this, newState);
				}
				state = newState;
			}
		}
		
		override public function dispose():void {
			changeStateFunc = null;
			super.dispose();
		}
		
		/**
		 * Задает слушателя для события MouseEvent.CLICK
		 * 
		 * @param	func		Функция обработчик
		 * @param	data		Задает значение данных
		 */
		public function addClickListener(func:Function, data:Object = null):void {
			if (data != null) {
				this.data = data;
			}
			addListener(MouseEvent.CLICK, func);
		}
		
		/**
		 * Эмулирует клик по кнопке
		 */
		public function click():void {
			dispatchEvent(new MouseEvent(MouseEvent.CLICK));
		}
		
		/**
		 * Добавить вариантное событие
		 * 
		 * @param	dispatcher		Определеяет значение свойства dispatcher
		 * @param	variance		Тип варианта
		 * @param	data			Задает значение данных (свойство data), только если data != null
		 */
		public function addVarianceListener(dispatcher:EventDispatcher, variance:uint, data:Object = null):void {
			this.dispatcher = dispatcher;
			this.variance = variance;
			if (data != null) {
				this.data = data;
			}
			addListener(MouseEvent.CLICK, onVariance);
		}
		
		protected function onVariance(event:MouseEvent = null):void {
			dispatchVarianceEvent(variance, data);
		}

		override public function set mouseEnabled(enabled:Boolean):void {
			if (!enabled) {
				if (state != UP && state != DISABLED) {
					changeState(UP);
				}
			}
			super.mouseEnabled = enabled;
		}

		private static const
			downTransform:ColorTransform = new ColorTransform(0.9, 0.9, 0.9),
			upTransform:ColorTransform = new ColorTransform()
			;
		public static function defaultButtonChangeState(bt:VButton, newState:uint):void {
			if (newState == VButton.DISABLED) {
				bt.filters = VSkin.GREY_FILTER;
			} else {
				bt.filters = null;
				if (newState == VButton.DOWN) {
					bt.transform.colorTransform = downTransform;
				} else {
					bt.transform.colorTransform = upTransform;
					if (newState == VButton.OVER) {
						bt.filters = VSkin.CONTRAST_FILTER;
					}
				}
			}
		}

		public static function mcButtonChangeState(bt:VButton, newState:uint):void {
			if (newState == OVER || newState == DISABLED) {
				bt.filters = (newState == OVER) ? VSkin.CONTRAST_FILTER : VSkin.GREY_FILTER;
				if (bt.state != DOWN) {
					return;
				}
			} else {
				bt.filters = null;
			}
			((bt.skin as VSkin).content as MovieClip).gotoAndStop(newState == DOWN ? '_down' : '_up');
		}

		/**
		 * Создать кнопку
		 * Универсальный метод
		 *
		 * @param    skin                Скин
		 * @param    icon                Иконка
		 * @param    iconLayout          Layout-иконки
		 * @param    changeStateFunc
		 * @return
		 */
		public static function create(skin:VComponent, icon:VComponent = null, iconLayout:Object = null, changeStateFunc:Function = null):VButton {
			var bt:VButton = new VButton();
			bt.setSkin(skin);
			if (icon) {
				bt.setIcon(icon, iconLayout);
			}
			if (changeStateFunc != null) {
				bt.changeStateFunc = changeStateFunc;
			}
			return bt;
		}

		/**
		 * Создать кнопку на базе embed-скина
		 * Кнопка принимает размер скина
		 *
		 * @param    skinName            Имя скина
		 * @param    skinMode            Режим скина
		 * @param    icon                Иконка
		 * @param    iconLayout          Layout-иконки
		 * @param    changeStateFunc
		 * @return
		 */
		public static function createEmbed(skinName:String, skinMode:uint = 0, icon:VComponent = null, iconLayout:Object = null, changeStateFunc:Function = null):VButton {
			var skin:VSkin = SkinManager.getEmbed(skinName, skinMode);
			var bt:VButton = new VButton();
			bt.setSize(skin.measuredWidth, skin.measuredHeight);
			bt.setSkin(skin);
			if (icon) {
				bt.setIcon(icon, iconLayout);
			}
			if (changeStateFunc != null) {
				bt.changeStateFunc = changeStateFunc;
			}
			return bt;
		}

	} //end class
}