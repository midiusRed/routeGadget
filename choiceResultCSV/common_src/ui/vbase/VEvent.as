package ui.vbase {
	import flash.events.Event;
	
	public class VEvent extends Event {
		public static const
			SCROLL:String = 'vScroll',
			SELECT:String = 'vSelect',
			CHANGE:String = 'vChange',
			VARIANCE:String = 'vVariance',
			COMPLETE:String = 'vComplete',
			CLOSE:String = 'vClose'
			;
		public var
			variance:uint,
			data:*
			;
		
		public function VEvent(type:String, data:* = null, variance:uint = 0) {
			super(type);
			this.data = data;
			this.variance = variance;
		}

	} //end class
}