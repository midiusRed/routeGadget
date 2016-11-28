package ui.vbase {
	import flash.display.Graphics;
	import flash.display.Shape;

	public class VProgressBar extends VComponent {
		public static const
			MASK:uint = 1,
			FLIP:uint = 2,
			EMBED:uint = 4
			;
		protected var
			_value:Number = 0,
			indicator:VSkin
			;

		public function VProgressBar(indicator:VSkin, indicatorLayout:Object = null, mode:uint = 0) {
			mouseChildren = false;
			CONFIG::debug {
				mode |= V_TOOL_SOLID;
			}
			this.mode = mode;
			this.indicator = indicator;
			add(indicator, indicatorLayout);

			if ((mode & MASK) != 0) {
				addChild(indicator.mask = new Shape());
			}
		}
		
		protected function updateIndicator():void {
			var w:Number = Math.round(indicator.w * _value);
			if ((mode & MASK) != 0) {
			    syncMask((indicator.mask as Shape).graphics, w);
			} else {
				if ((mode & EMBED) != 0) {
					indicator.content.width = w;
				} else {
					indicator.width = w;
				}
				if ((mode & FLIP) != 0) {
					indicator.x = this.w - w;
				}
			}
		}

		private function syncMask(g:Graphics, w:Number):void {
			g.clear();
			g.beginFill(0);
			g.drawRect((mode & FLIP) != 0 ? this.w - w : 0, 0, w, indicator.h);
		}

		public function getIndicator():VSkin {
			return indicator;
		}
		
		public function set value(v:Number):void {
			if (v < 0) {
				v = 0;
			} else if (v > 1) {
				v = 1;
			}
			_value = v;
			if (isGeometryPhase && visible) {
				updateIndicator();
			}
		}
		
		public function get value():Number {
			return _value;
		}
		
		override protected function customUpdate():void {
			super.customUpdate();
			if ((mode & MASK) != 0) {
				indicator.mask.x = indicator.x;
				indicator.mask.y = indicator.y;
			}
			updateIndicator();
		}

		CONFIG::debug
		override public function getToolPropList(out:Array):void {
			out.push(
				new VOComponentItem('value', VOComponentItem.DIGIT, Math.round(_value * 100))
			);
		}

		CONFIG::debug
		override public function updateToolProp(item:VOComponentItem):void {
			if (item.key == 'value') {
				value = item.valueInt / 100;
			}
		}

	} //end class
}