package ui.vbase {

	public class VLayoutPanel extends VComponent {
		public var
			updateFunc:Function,
			calcContentFunc:Function
			;

		public function VLayoutPanel(updateFunc:Function, calcContentFunc:Function = null) {
			this.updateFunc = updateFunc;
			this.calcContentFunc = calcContentFunc;
		}

		override protected function syncChildLayout(component:VComponent):void {
			syncContentSize(true);
		}

		public function setContentSize(w:uint, h:uint):void {
			contentW = w;
			contentH = h;
		}

		override protected function calcContentSize():void {
			if (calcContentFunc != null) {
				calcContentFunc(this);
			} else {
				super.calcContentSize();
			}
		}

		override protected function customUpdate():void {
			if (updateFunc != null) {
				updateFunc(this);
			} else {
				super.customUpdate();
			}
		}

	} //end class
}