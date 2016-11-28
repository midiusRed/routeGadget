package ui.vbase {
	import flash.display.Bitmap;
	import flash.display.BitmapData;
	import flash.display.DisplayObject;
	import flash.display.Loader;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.system.ImageDecodingPolicy;
	import flash.system.LoaderContext;
	import flash.text.engine.FontLookup;
	import flash.text.engine.TextBaseline;
	import flash.utils.getDefinitionByName;

	import flashx.textLayout.elements.Configuration;
	import flashx.textLayout.elements.InlineGraphicElement;
	import flashx.textLayout.elements.TextFlow;
	import flashx.textLayout.formats.TextLayoutFormat;
	import flashx.textLayout.formats.WhiteSpaceCollapse;

	/**
	 * Менеджер скинов
	 */
	public class SkinManager {
		public static const
			LOAD_CLIP:uint = 1,
			NO_CACHE:uint = 2,
			PNG:uint = 4,
			JPG:uint = PNG | 8,
			externalDispatcher:EventDispatcher = new EventDispatcher()
			;
		private static const swfCache:Object = {};
		public static var url:String;

		public static function init(externalUrl:String):TextLayoutFormat {
			url = externalUrl;

			XML.ignoreProcessingInstructions = false;
			XML.ignoreWhitespace = false;

			var config:Configuration = TextFlow.defaultConfiguration;
			config.inlineGraphicResolverFunction = SkinManager.inlineGraphicResolverFunction;
			config.manageTabKey = false;

			var format:TextLayoutFormat = config.textFlowInitialFormat as TextLayoutFormat;
			format.fontLookup = FontLookup.EMBEDDED_CFF;
			//format.lineHeight = '120%';
			format.whiteSpaceCollapse = WhiteSpaceCollapse.PRESERVE;

			AssetLoader.imageContext = new LoaderContext();
			AssetLoader.policyImageContext.imageDecodingPolicy = AssetLoader.imageContext.imageDecodingPolicy = ImageDecodingPolicy.ON_LOAD;

			return format;
		}

		/**
		 * Применить вложенный скин
		 *
		 * @param	target				Объект VSkin, куда будет помещен скин
		 * @param	skinName			Имя вложенного скина
		 */
		public static function applyEmbed(target:VSkin, skinName:String):void {
			try {
				var clsSkin:Class = getDefinitionByName('ESkins.' + skinName) as Class;
				var skin:Object = new clsSkin();
			} catch (error:ReferenceError) {
			}
			target.applyContent(skin);
		}

		public static function getBitmapData(skinName:String):BitmapData {
			try {
				var clsSkin:Class = getDefinitionByName('ESkins.' + skinName) as Class;
				var bd:BitmapData = new clsSkin() as BitmapData;
			} catch (error:ReferenceError) {
			}
			if (!bd) {
				bd = new BitmapData(3, 3, false, 0xFF0000);
			}
			return bd;
		}

		/**
		 * Получить встроенный скин
		 *
		 * @param	skinName			Имя скина
		 * @param	mode				Режимы работы скина см описание констант в VSkin
		 * @return
		 */
		public static function getEmbed(skinName:String, mode:uint = 0):VSkin {
			var target:VSkin = new VSkin(mode);
			applyEmbed(target, skinName);
			return target;
		}

		/**
		 * Применить внешний скин
		 *
		 * @param	target				Объект VSkin, куда будет помещен скин
		 * @param	packName			Имя пакета
		 * @param	skinName			Имя внешнего скина (опционально, для картинки не юзается)
		 * @param	externalMode		Режимы загрузки внешних скинов
		 */
		public static function applyExternal(target:VSkin, packName:String, skinName:String = null, externalMode:uint = 0):void {
			CONFIG::debug {
				if (!packName) {
					throw new Error();
				}
			}

			var isImage:Boolean = (externalMode & PNG) != 0;
			if (isImage) {
				packName += (externalMode & JPG) == JPG ? '.jpg' : '.png';
			}

			var data:Object = swfCache[packName];
			//скин загрузить не удалось || скин уже загружен
			if (data === false || data is Loader) {
				target.applyContent(getCopyExternal(packName, skinName));
			} else {
				target.setExternalInterest(new VOExternalInfo(packName, skinName));

				if (data == null) { //скин еще не загружался
					var assetLoader:AssetLoader = new AssetLoader();
					if ((externalMode & NO_CACHE) == 0) {
						swfCache[packName] = true;
					}
					assetLoader.packName = packName;
					assetLoader.init(onExternalLoad);
					assetLoader.loadUrl(url + (isImage ? 'images/' + packName : 'swfs/' + packName + '.swf'), !isImage);
				}

				if ((externalMode & LOAD_CLIP) != 0) {
					target.useLoadClip();
				}
			}
		}

		public static function loadSwf(packName:String):void {
			if (swfCache[packName] == null) {
				var assetLoader:AssetLoader = new AssetLoader();
				swfCache[packName] = true;
				assetLoader.packName = packName;
				assetLoader.init(onExternalLoad);
				assetLoader.loadUrl(url + 'swfs/' + packName + '.swf', true);
			}
		}

		/**
		 * Получить внешний скин
		 *
		 * @param	skinName				Имя скина
		 * @param	externalMode			Режимы загрузки внешних скинов
		 * @param	skinMode				Режимы работы скина см описание констант в VSkin
		 * @return
		 */
		public static function getExternal(skinName:String, externalMode:uint = 0, skinMode:uint = 0):VSkin {
			var target:VSkin = new VSkin(skinMode);
			applyExternal(target, skinName, null, externalMode);
			return target;
		}

		/**
		 * Получить внешний пакетный скин
		 *
		 * @param	packName				Имя пакета
		 * @param	skinName				Имя скина
		 * @param	skinMode				Режимы работы скина см описание констант в VSkin
		 * @param	externalMode			Режимы загрузки внешних скинов
		 * @param	externalHandler			Будет вызван ТОЛЬКО если сейчас идет загрузка
		 * @return
		 */
		public static function getPack(packName:String, skinName:String, skinMode:uint = 0, externalMode:uint = 0, externalHandler:Function = null):VSkin {
			var target:VSkin = new VSkin(skinMode);
			applyExternal(target, packName, skinName, externalMode);
			if (externalHandler != null && !target.isContent) {
				target.setMode(VSkin.EXTERNAL_EVENT);
				target.addEventListener(VEvent.COMPLETE, externalHandler);
			}
			return target;
		}

		/**
		 * Вставляет скин внутрь дочернего объекта контейнера
		 *
		 * @param	container			Контейнер, в рамках которого будет поиск целевого объекта, в который будет произведена вставка
		 * @param	boxName				Имя целевого объекта
		 * @param	skin				Вставляемый скин
		 */
		public static function addInsideContainer(container:Sprite, boxName:String, skin:DisplayObject):void {
			for (var i:int = container.numChildren - 1; i >= 0; i--) {
				var obj:DisplayObject = container.getChildAt(i);
				if (obj.name == boxName) {
					if (obj is Sprite) {
						(obj as Sprite).addChild(skin);
					}
					break;
				}
			}

			if (skin is VComponent) {
				(skin as VComponent).geometryPhase();
			}
		}

		/**
		 * Копировать уже загруженный внешний скин
		 *
		 * @param	packName	Имя пакета
		 * @param	skinName	Имя скина внутри пакета || null
		 * @return				BitmapData || DisplayObject || null
		 */
		public static function getCopyExternal(packName:String, skinName:String):Object {
			var loader:Loader = swfCache[packName] as Loader;
			if (loader) {
				try {
					if (loader.content is Bitmap) {
						return (loader.content as Bitmap).bitmapData;
					} else {
						var clsSkin:Class = loader.contentLoaderInfo.applicationDomain.getDefinition('Skins.' + (skinName ? skinName : packName)) as Class;
						return new clsSkin();
					}
				} catch (error:ReferenceError) {
				}
			}
			return null;
		}

		/**
		 * Обработчик завершения загрузки внешних графических ресурсов
		 *
		 * @param	assetLoader			Объект AssetLoader, который производил загрузку
		 */
		public static function onExternalLoad(assetLoader:AssetLoader):void {
			swfCache[assetLoader.packName] = assetLoader.isError ? false : assetLoader.loader;
			externalDispatcher.dispatchEvent(new Event(assetLoader.packName));
		}

		//формат img@source:
		//   lib,name[,skinMode]
		//   ext,name[,extMode][,skinMode]
		//   pack,packName,skinName[,extMode][,skinMode]
		public static function inlineGraphicResolverFunction(element:InlineGraphicElement):VSkin {
			element.dominantBaseline = TextBaseline.IDEOGRAPHIC_CENTER;

			var src:String = element.source as String;

			if (element.width is uint) {
				var w:uint = element.width as uint;
			}
			if (element.height is uint) {
				var h:uint = element.height as uint;
			}

			var ar:Array = src.split(',');
			var len:uint = ar.length;

			var skin:VSkin = new VSkin();
			if (len >= 2) {
				if (ar[0] == 'lib') {
					if (len > 2) {
						skin.setMode(ar[2]);
					}
					applyEmbed(skin, ar[1]);
				} else if (ar[0] == 'pack' && len > 2) {
					if (len > 4) {
						skin.setMode(ar[4]);
					}
					applyExternal(skin, ar[1], ar[2], len > 3 ? ar[3] : 0);
				} else {
					applyExternal(skin, ar[1], null, len > 2 ? ar[2] : 0);
				}
			}
			if (skin.isContent) {
				skin.setMode(VSkin.LEFT);
			}
			skin.setGeometrySize(w, h, true);

			//если скин загружен и если есть зазор справа то уберем его для более красивого прилегания текста к иконке
			if (skin.isContent && skin.width < w) {
				w = Math.ceil(skin.width);
				element.width = w;
			}
			skin.graphics.beginFill(0, 0);
			skin.graphics.drawRect(0, 0, w, h);

			if (element.locale) {
				skin.hint = element.locale;
				skin.mouseEnabled = true;
				element.locale = undefined;
			}

			return skin;
		}

	} //end class
}