package ui.vbase {
	import flash.events.MouseEvent;

	public class VRenderer extends VComponent {
		public var dataIndex:uint;
		
		public function setData(data:Object):void {
		}

		public function setSelected(flag:Boolean):void {
		}

		/**
		 * Добавить срабатывание выбора при клике по компоненту
		 * Клик генерирует новое сообщение VEvent.SELECT со стороны рендерера, который обрабатывается VGrid
		 *
		 * @param  clickComponent  Цель клика
		 */
		public function addSelectTrigger(clickComponent:VComponent):void {
			clickComponent.addListener(MouseEvent.CLICK, onSelectTrigger);
		}

		private function onSelectTrigger(event:MouseEvent):void {
			dispatcher.dispatchEvent(new VEvent(
				VEvent.SELECT,
				(event.currentTarget is VButton) ? (event.currentTarget as VButton).data : null,
				dataIndex
			));
		}

	} //end class
}