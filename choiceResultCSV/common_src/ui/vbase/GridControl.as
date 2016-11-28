package ui.vbase {
	import flash.events.MouseEvent;

	public class GridControl {
		public static const
			NAV_BT_VISIBLE:uint = 1,
			NAV_BT_DISABLED:uint = 2,
			NAV_SMART:uint = NAV_BT_VISIBLE | NAV_BT_DISABLED,
			PAGER_VISIBLE:uint = 4,
			SMART:uint = NAV_BT_VISIBLE | NAV_BT_DISABLED | PAGER_VISIBLE,
			NAV_VERTICAL:uint = 4096
			;
		public var
			grid:VGrid,
			scrollBar:VScrollBar,
			pager:IPager,
			prevBt:VButton,
			nextBt:VButton,
			navBtFactory:Function, //(isFlip, isVertical)
			pagerFactory:Function
			;
		protected var mode:uint;
		private var
			addNavBtFunc:Function,
			addPagerFunc:Function
			;

		public function GridControl(grid:VGrid, mode:uint = 0) {
			this.mode = mode;
			assignGrid(grid);
		}

		public function dispose():void {
			assignNavButtons();
			assignPager(null);
			assignScrollBar(null);
			resetGrid();
		}

		public function assignGrid(grid:VGrid):void {
			resetGrid();
			this.grid = grid;
			grid.control = this;
			grid.addListener(VEvent.CHANGE, onChangeIndex);
		}

		public function resetGrid():void {
			if (grid) {
				grid.removeListener(VEvent.CHANGE, onChangeIndex);
				grid.control = null;
				grid = null;
			}
		}

		public function onChangeIndex(event:VEvent):void {
			if ((mode & GridControl.NAV_BT_VISIBLE) != 0) {
				if (!nextBt && grid.isPages) {
					createNavBt();
				}
			}
			if ((mode & GridControl.PAGER_VISIBLE) != 0) {
				if (!pager && grid.isPages) {
					createPager();
				}
			}
			if (pager) {
				syncPager();
			}
			if (prevBt || nextBt) {
				syncNavButton();
			}
			if (scrollBar) {
				syncScrollBar();
			}
		}

		//---Pager---

		public function assignPager(pager:IPager):void {
			if (this.pager) {
				this.pager.setSelectListener(null);
			}
			this.pager = pager;
			if (pager) {
				pager.setSelectListener(onChangePage);
				syncPager();
			}
		}

		//сменилась страница
		private function onChangePage(event:VEvent):void {
			grid.index = uint(event.data) * grid.maxRenderer;
		}

		protected function syncPager():void {
			var num:uint = grid.maxRenderer;
			var showCount:uint = Math.ceil(grid.length / num);
			pager.setParam(Math.ceil(grid.index / num), showCount);
			if ((mode & PAGER_VISIBLE) != 0) {
				pager.visible = grid.length > 0;
			}
		}

		//---Navigate buttons---
		
		public function assignNavButtons(prevBt:VButton = null, nextBt:VButton = null):void {
			if (this.prevBt) {
				this.prevBt.removeListener(MouseEvent.CLICK, onNavButton);
				this.prevBt.visible = true;
			}
			this.prevBt = prevBt;
			if (prevBt) {
				prevBt.addClickListener(onNavButton);
			}
			
			if (this.nextBt) {
				this.nextBt.removeListener(MouseEvent.CLICK, onNavButton);
				this.nextBt.visible = true;
			}
			this.nextBt = nextBt;
			if (nextBt) {
				nextBt.addClickListener(onNavButton);
			}
			if (prevBt || nextBt) {
				syncNavButton();
			}
		}
		
		private function onNavButton(event:MouseEvent):void {
			var max:uint = grid.length;
			var index:uint = grid.index;
			var bValue:uint = grid.maxRenderer;

			if (event.currentTarget == prevBt) {
				if (bValue > index) {
					if (index == 0) {
						index = uint(max / bValue) * bValue;
					} else {
						index = 0;
					}
				//если USE_END_LIMIT != 0 и FLOAT_INDEX == 0, то в случае не кратности длины списка (max % bValue != 0) возникает проблема пропуска элементов
				//при использовании действия назад на последней странице (index >= max - bValue)
				} else if ((grid.getMode() & VGrid.USE_END_LIMIT) != 0 && index >= max - bValue && max % bValue != 0 && (grid.getMode() & VGrid.FLOAT_INDEX) == 0) {
					index = uint(index / bValue) * bValue;
				} else {
					index -= bValue;
				}
			} else if (index + bValue >= max) {
				index = 0;
			} else {
				index += bValue;
			}
			grid.index = index;
		}

		protected function syncNavButton():void {
			var useVisible:Boolean = (mode & NAV_BT_VISIBLE) != 0;
			var useDisabled:Boolean = (mode & NAV_BT_DISABLED) != 0;
			if (prevBt) {
				if (useVisible) {
					prevBt.visible = grid.isPages;
				}
				if (useDisabled) {
					prevBt.disabled = grid.index == 0;
				}
			}
			if (nextBt) {
				if (useVisible) {
					nextBt.visible = grid.isPages;
				}
				if (useDisabled) {
					nextBt.disabled = grid.index >= grid.length - grid.maxRenderer;
				}
			}
		}

		//---ScrollBar---
		
		public function assignScrollBar(scrollBar:VScrollBar):void {
			if (this.scrollBar) {
				this.scrollBar.removeListener(VEvent.SCROLL, onScroll);
			}
			this.scrollBar = scrollBar;
			if (scrollBar) {
				scrollBar.addListener(VEvent.SCROLL, onScroll);
				syncScrollBar();
			}
		}
		
		private function onScroll(event:VEvent):void {
			grid.index = uint(event.data);
		}

		protected function syncScrollBar():void {
			if (grid.length != scrollBar.getMax() || grid.maxRenderer != scrollBar.getPageSize()) {
				scrollBar.setEnv(grid.maxRenderer, grid.length, grid.index);
			} else {
				scrollBar.value = grid.index;
			}
		}

		private function createNavBt():void {
			if (navBtFactory == null) {
				return;
			}
			var isVertical:Boolean = (mode & NAV_VERTICAL) != 0;
			var prevBt:VButton = navBtFactory(false, isVertical);
			var nextBt:VButton = navBtFactory(true, isVertical);
			if (addNavBtFunc != null) {
				addNavBtFunc(prevBt, nextBt);
			}
			assignNavButtons(prevBt, nextBt);
		}

		private function createPager():void {
			if (pagerFactory == null) {
				return;
			}
			var pager:IPager = pagerFactory();
			if (addPagerFunc != null) {
				addPagerFunc(pager);
			}
			assignPager(pager);
		}

		public static function assign(grid:VGrid, mode:uint, navBtFactory:Function, addNavBtFunc:Function, pagerFactory:Function = null, addPagerFunc:Function = null):GridControl {
			var connector:GridControl = new GridControl(grid, mode);
			connector.navBtFactory = navBtFactory;
			var flag:Boolean = grid.length > grid.maxRenderer;
			if (addNavBtFunc != null) {
				connector.addNavBtFunc = addNavBtFunc;
				if (flag || (mode & GridControl.NAV_BT_VISIBLE) == 0) {
					connector.createNavBt();
				}
			}
			connector.pagerFactory = pagerFactory;
			if (addPagerFunc != null) {
				connector.addPagerFunc = addPagerFunc;
				if (flag || (mode & GridControl.PAGER_VISIBLE) == 0) {
					connector.createPager();
				}
			}
			return connector;
		}

		public function setVisible(value:Boolean):void {
			if (prevBt) {
				prevBt.visible = value;
			}
			if (nextBt) {
				nextBt.visible = value;
			}
			if (pager) {
				pager.visible = value;
			}
			if (scrollBar) {
				scrollBar.visible = value;
			}
		}
		
	} //end class
}